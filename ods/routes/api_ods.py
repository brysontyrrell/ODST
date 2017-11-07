import base64
import json
import os
import urlparse

import flask
from flask.blueprints import Blueprint
from sqlalchemy.exc import IntegrityError as saIntError
from pymysql import IntegrityError as myIntErr

from .shared import server_data, package_json, packages_json
from ..database import db
from ..database.api import get_server_data, new_notified_package
from ..database.models import RegisteredODS
from ..tasks.sync import download_package
from ..api_clients.ods_client import ODSClient
from ..security.auth import ods_auth_required
from ..security.cipher import AESCipher

blueprint = Blueprint('ods_api', __name__, url_prefix='/api/ods')


@blueprint.route('/about')
@ods_auth_required
def about():
    return server_data()


@blueprint.route('/register', methods=['POST'])
@ods_auth_required(fail_on_lookup=False)
def register_a_ods():
    flask.current_app.logger.info('Request to register a remote ODS received...')
    token = flask.g.auth_token
    flask.current_app.logger.debug('Token received: {}'.format(token))

    # Verify the 'iss', 'iss_key', and 'iss_url' claims have been provided
    if not all(key in token.keys() for key in ('iss', 'iss_data')):
        flask.abort(400)

    # Validate the remote key was encrypted with this ODS's key
    # This should be moved into a sub-function
    flask.current_app.logger.info("Decrypting registering ODS's data...")
    key_cipher = AESCipher(get_server_data().key)

    remote_ods = json.loads(key_cipher.decrypt(token['iss_data']))
    flask.current_app.logger.debug(remote_ods)
    decoded_key = base64.b64decode(remote_ods['key'])
    try:
        assert len(decoded_key) == 32
    except AssertionError as err:
        flask.current_app.logger.exception(err)
        flask.current_app.logger.error('The remote key is invalid.')
        flask.abort(403)

    def remote_ods_url():
        if not remote_ods['url']:
            # REMOVE THIS ONCE UI ALLOWS SERVER EDITING
            if flask.request.headers.getlist("X-Forwarded-For"):
                ip_addr = flask.request.headers.getlist("X-Forwarded-For")[0]
            else:
                ip_addr = flask.request.remote_addr

            return urlparse.urlunparse(('http', ip_addr, '', '', '', ''))
        else:
            return remote_ods['url']

    cipher = AESCipher()

    registering_ods = RegisteredODS(
        iss=token['iss'],
        url=remote_ods_url(),
        key_encrypted=cipher.encrypt(decoded_key),
        name=remote_ods['name'],
        stage=remote_ods['stage'],
        firewalled_mode=remote_ods['firewalled_mode']
    )

    flask.current_app.logger.info('Saving to database...')
    try:
        db.session.add(registering_ods)
        db.session.commit()
        flask.current_app.logger.debug(registering_ods.serialize)
    except (saIntError, myIntErr) as err:
        flask.current_app.logger.error(err)
        flask.abort(409)

    return '', 201


@blueprint.route('/command', methods=['POST'])
@ods_auth_required
def package_alert():
    # This is going to be a filtering function to parse all the different
    # possible commands that could be sent. These commands may need to be
    # made into queued tasks.
    if not flask.request.is_json:
        pass

    data = flask.request.get_json()

    # A POST from a registered JDS about a newly uploaded package
    if data['command'] == 'new_package':
        new_package(data)

    return '', 202


def new_package(command):
    """
    {
        'command': 'new_package',
        'package_id': 1
    }
    :return:
    """
    ods = flask.g.ods_object
    flask.current_app.logger.info(
        'New Package: Received notification from {}'.format(ods.iss))

    client = ODSClient(ods)

    flask.current_app.logger.info(
        'New Package: Requesting package data from ODS: {}'.format(ods.iss))
    package_data = client.get_package(command['package_id'])
    package = new_notified_package(package_data)

    flask.current_app.logger.info(
        'New Package: Filename: {}'.format(package.filename))

    staging_dir = os.path.join(
        flask.current_app.config['UPLOAD_STAGING_DIR'], package.uuid)
    os.mkdir(staging_dir)

    flask.current_app.logger.info(
        'New Package: Created staging directory: {}'.format(staging_dir))

    flask.current_app.logger.info(
        'New Package: Sending package to download queue...')
    download_package.delay(package.id, ods.iss)


@blueprint.route('/packages')
def list_packages():
    return packages_json()


@blueprint.route('/packages/<package_id_or_name>')
def get_package(package_id_or_name):
    return package_json(package_id_or_name)
