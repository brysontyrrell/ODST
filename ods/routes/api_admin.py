import base64
from datetime import datetime

import flask
from flask.blueprints import Blueprint
import psutil
from werkzeug.utils import secure_filename

from .shared import packages_json, server_data
from ..exc import ODSAuthenticationError, RemoteRegistrationFailed
from ..database.api import (
    all_registered_ods, new_registered_ods,
    update_registered_ods, new_uploaded_package
)
from ..api_clients.ods_client import ODSClient
from ..ods_files import move_staging_to_static
from ..utilities import human_readable_bytes, human_readable_time, parse_url

blueprint = Blueprint('api_admin', __name__, url_prefix='/api/admin')


@blueprint.errorhandler(409)
def admin_error_conflict(error):
    flask.current_app.logger.error(error)
    flask.flash(
        'The action failed! There was a conflict with an existing resource.')
    return flask.jsonify(
        {'error': 'There was a conflict with an existing resource.'}), 409


@blueprint.route('/about')
def about():
    return server_data()


@blueprint.route('/system')
def system():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(flask.current_app.config['APP_DIR'])
    network = psutil.net_io_counters()
    uptime = int((datetime.utcnow() - datetime.utcfromtimestamp(
        psutil.boot_time())).total_seconds())

    data = {
        'cpu_count': int(psutil.cpu_count()),
        'mem_total': int(mem.total),
        'mem_total_hr': human_readable_bytes(int(mem.total)),
        'mem_used': int(mem.used),
        'mem_used_hr': human_readable_bytes(int(mem.used)),
        'mem_available': int(mem.available),
        'mem_available_hr': human_readable_bytes(int(mem.available)),
        'disk_total': int(disk.total),
        'disk_total_hr': human_readable_bytes(int(disk.total)),
        'disk_used': int(disk.used),
        'disk_used_hr': human_readable_bytes(int(disk.used)),
        'disk_free': int(disk.free),
        'disk_free_hr': human_readable_bytes(int(disk.free)),
        'network_bytes_sent': int(network.bytes_sent),
        'network_bytes_sent_hr': human_readable_bytes(int(network.bytes_sent)),
        'network_bytes_received': int(network.bytes_recv),
        'network_bytes_received_hr': human_readable_bytes(
            int(network.bytes_recv)),
        'uptime': uptime,
        'uptime_hr': human_readable_time(uptime)
    }

    return flask.jsonify(data), 200


@blueprint.route('/packages')
def list_packages():
    return packages_json()


@blueprint.route('/registered_ods')
def list_registered_ods():
    ods_json = {'items': [ods.serialize for ods in all_registered_ods()]}
    return flask.jsonify(ods_json), 200


@blueprint.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = flask.request.files['file']
    stage = flask.request.form.get('stage')

    flask.current_app.logger.info(
        'Package Upload: Saving package objects to database...')
    package = new_uploaded_package(uploaded_file, stage)
    filename = secure_filename(package.filename)

    flask.current_app.logger.info(
        'Package Upload: Moving from staging to static (Public)...')
    move_staging_to_static(filename)

    # Need to include functionality here for: notify JDSs queue task
    ods_to_notify = all_registered_ods()
    for ods in ods_to_notify:
        flask.current_app.logger.info(
            'Package Upload: Sending new package notification to ODS: '
            '{}'.format(ods.iss))
        client = ODSClient(ods)
        client.send_command({'command': 'new_package', 'package_id': package.id})

    return flask.jsonify(
        {'filename': filename, 'sha1': package.sha1}), 201


@blueprint.route('/register', methods=['POST'])
def register_ods():
    flask.current_app.logger.info(
        'ODS Registration: Admin initiated registration action...')
    data = flask.request.get_json()
    flask.current_app.logger.debug(data)

    try:
        url = parse_url(data['url'])
    except ValueError as err:
        flask.flash(err.message)
        raise RemoteRegistrationFailed

    try:
        decoded_key = base64.b64decode(data['key'])
    except TypeError:
        flask.flash('Key must be Base64 encoded!')
        raise RemoteRegistrationFailed

    if len(decoded_key) != 32:
        flask.flash('Invalid key provided!')
        raise RemoteRegistrationFailed

    ods = new_registered_ods(data['iss_id'], decoded_key, url)
    client = ODSClient(ods)

    flask.current_app.logger.info('Performing registration with remote ODS...')
    client.register_with()

    flask.current_app.logger.info('Updating registered ODS data...')
    update_registered_ods(ods, **client.about())

    flask.current_app.logger.info('Remote ODS registration complete!')
    return flask.jsonify({}), 200
