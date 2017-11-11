import base64
from datetime import datetime

import flask
from flask.blueprints import Blueprint
import psutil

from .shared import server_data, package_json, packages_json
from ..exc import RemoteRegistrationFailed
from ..database.api import (
    all_registered_ods, new_registered_ods,
    update_registered_ods, new_uploaded_package,
    update_server_data
)
from ..api_clients.ods_client import ODSClient
from ..ods_files import move_staging_to_static
from ..tasks.notifications import send_new_package_command
from ..utilities import human_readable_bytes, human_readable_time, parse_url

blueprint = Blueprint('api_admin', __name__, url_prefix='/api/admin')


@blueprint.errorhandler(409)
def admin_error_conflict(error):
    flask.current_app.logger.error(error)
    flask.flash(
        'The action failed! There was a conflict with an existing resource.')
    return flask.jsonify(
        {'error': 'There was a conflict with an existing resource.'}), 409


@blueprint.route('/about', methods=['GET'])
def about():
    """Returns ODS application settings.

    .. :quickref: About; Returns ODS application settings.

    **Example Request:**

    .. sourcecode:: http

        GET /api/admin/about HTTP/1.1
        Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "firewalled_mode": false,
            "iss": "e7becdda9a9046f6a78f69ef591e9835",
            "key": "r3Yt354eDTY0JkaiObpsM4krfkDzdZD9NNYwDr9aSk0=",
            "name": "Example ODS",
            "stage": "Prod",
            "url": "http://192.168.99.100"
        }

    """
    return server_data()


@blueprint.route('/about/update', methods=['POST'])
def about_update():
    """Updates ODS application information and settings.

    .. note::

        You cannot update the ``iss`` or ``key`` values!

    Accepted values for ``stage`` are: ``Dev``, ``Test``, ``Prod``

    Accepted values for ``firewalled_mode`` are: ``Enabled``, ``Disabled``

    .. :quickref: About; Updates ODS application settings.

    **Example Request:**

    .. sourcecode:: http

        POST /api/admin/about HTTP/1.1
        Content-Type: application/json

        {
            "name": "Example ODS",
            "url": "http://192.168.99.100",
            "firewalled_mode": "Disabled",
            "stage": "Prod"
        }

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 201 OK
        Content-Type: text/html

    """
    flask.current_app.logger.info('Updating server information...')
    data = flask.request.get_json()
    update_server_data(**data)
    return '', 201


@blueprint.route('/system', methods=['GET'])
def system():
    """Returns system information.

    ``disk_``, ``mem_``, and ``network_`` values are represented in total bytes.

    ``uptime`` is represented in total seconds.

    Human readable values are denoted by the ``_hr`` suffix.

    .. :quickref: System; Returns system information.

    **Example Request:**

    .. sourcecode:: http

        GET /api/admin/system HTTP/1.1
        Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "cpu_count": 2,
            "disk_free": 60352081920,
            "disk_free_hr": "56.2 GB",
            "disk_total": 67371577344,
            "disk_total_hr": "62.7 GB",
            "disk_used": 3566796800,
            "disk_used_hr": "3.3 GB",
            "mem_available": 936255488,
            "mem_available_hr": "892.9 MB",
            "mem_total": 1567678464,
            "mem_total_hr": "1.5 GB",
            "mem_used": 444342272,
            "mem_used_hr": "423.8 MB",
            "network_bytes_received": 54346,
            "network_bytes_received_hr": "53.1 KB",
            "network_bytes_sent": 45694,
            "network_bytes_sent_hr": "44.6 KB",
            "uptime": 30806,
            "uptime_hr": "8:33:26"
        }

    """
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


@blueprint.route('/packages', methods=['GET'])
def list_packages():
    """Returns a list of all packages on the server. The ``package objects`` are
    nested under an ``items`` key.

    ``created`` value is in ISO 8601 format (without microseconds).

    ``created_ts`` value is a Unix timestamp (time since Epoch).

    ``file_size`` value is represented in total bytes.

    ``file_size_hr`` is a human readable representation.

    .. :quickref: Packages; Returns a list of all packages on the server.

    **Example Request:**

    .. sourcecode:: http

        GET /api/admin/packages HTTP/1.1
        Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "items": [
                {
                    "created": "2017-11-11T03:15:54",
                    "created_ts": 1510370154,
                    "file_size": 3438044,
                    "file_size_hr": "3.3 MB",
                    "filename": "NoMAD.pkg",
                    "id": 1,
                    "sha1": "3fab53c6f12e3d4621b17f728e9b3c522bb90816",
                    "stage": "Prod",
                    "status": "Public",
                    "uuid": "28f7adde4f674873807a4c8c69b641d0"
                }
            ]
        }

    """
    return packages_json()


@blueprint.route('/packages/<package_id_or_name>', methods=['GET'])
def get_package(package_id_or_name):
    """Returns a single package by the database ID or filename.

    ``created`` value is in ISO 8601 format (without microseconds).

    ``created_ts`` value is a Unix timestamp (time since Epoch).

    ``file_size`` value is represented in total bytes.

    ``file_size_hr`` is a human readable representation.

    ``chunks`` is an array of indexed hashes for each 1 MB block of the file.

    .. :quickref: Packages; Returns a single package by the database ID or
        filename.

    **Example Request:**

    .. sourcecode:: http

        GET /api/admin/packages/1 HTTP/1.1
        Accept: application/json

    .. sourcecode:: http

        GET /api/admin/packages/NoMAD.pkg HTTP/1.1
        Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "created": "2017-11-11T03:15:54",
            "created_ts": 1510370154,
            "file_size": 3438044,
            "file_size_hr": "3.3 MB",
            "filename": "NoMAD.pkg",
            "id": 1,
            "sha1": "3fab53c6f12e3d4621b17f728e9b3c522bb90816",
            "stage": "Prod",
            "status": "Public",
            "uuid": "28f7adde4f674873807a4c8c69b641d0"
            "chunks": [
                {
                    "index": 0,
                    "sha1": "f34fef9be0364d92424106c19596d3fcd1676635"
                },
                {
                    "index": 1,
                    "sha1": "93633f00f71d3b5494b23b74b37777bc07f9d713"
                },
                {
                    "index": 2,
                    "sha1": "9e0ca33c872fb9b5d7aa46fbd865c309db792c12"
                },
                {
                    "index": 3,
                    "sha1": "468521469da7fd40ee72f18e70bf578f055b3878"
                }
            ],
        }

    """
    return package_json(package_id_or_name)


@blueprint.route('/registered_ods', methods=['GET'])
def list_registered_ods():
    """Returns a list of all registered ODS instances. The ``ods server
    objects`` are nested under an ``items`` key.

    ``registered_on`` value is in ISO 8601 format (without microseconds).

    ``registered_on_ts`` value is a Unix timestamp (time since Epoch).

    .. :quickref: ODS; Returns a list of all registered ODS instances.

    **Example Request:**

    .. sourcecode:: http

        GET /api/admin/registered_ods HTTP/1.1
        Accept: application/json

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "items": [
                {
                    "firewalled_mode": false,
                    "id": 1,
                    "name": "Example ODS 2",
                    "registered_on": "2017-11-10T04:45:47",
                    "registered_on_ts": 1510289147,
                    "stage": "Prod",
                    "url": "http://192.168.99.101"
                }
            ]
        }

    """
    ods_json = {'items': [ods.serialize for ods in all_registered_ods()]}
    return flask.jsonify(ods_json), 200


@blueprint.route('/register', methods=['POST'])
def register_ods():
    """Register with another ODS instance.

    .. :quickref: ODS; Register with another ODS instance.

    **Example Request:**

    .. sourcecode:: http

        POST /api/admin/register HTTP/1.1
        Content-Type: application/json

        {
            "url":"http://192.168.99.101",
            "iss_id":"e7becdda9a9046f6a78f69ef591e9835",
            "key":"r3Yt354eDTY0JkaiObpsM4krfkDzdZD9NNYwDr9aSk0="
        }

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 201 OK
        Content-Type: text/html

    """
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
    return '', 201


@blueprint.route("/upload", methods=["POST"])
def upload_file():
    """Upload a file to the ODS.

    Accepted values for ``stage`` are: ``Dev``, ``Test``, ``Prod``

    .. :quickref: Upload; Upload a file to the ODS.

    **Example Request:**

    .. sourcecode:: http

        POST /api/admin/register HTTP/1.1
        Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryvvcON8g8Lh1D16BS

        ------WebKitFormBoundaryvvcON8g8Lh1D16BS
        Content-Disposition: form-data; name="file"; filename="NoMAD.pkg"
        Content-Type: application/octet-stream

        ------WebKitFormBoundaryvvcON8g8Lh1D16BS
        Content-Disposition: form-data; name="stage"

        Prod
        ------WebKitFormBoundaryvvcON8g8Lh1D16BS--

    **Example Response:**

    .. sourcecode:: http

        HTTP/1.1 201 OK
        Content-Type: application/json

        {
            "filename": "NoMAD.pkg",
            "sha1": "3fab53c6f12e3d4621b17f728e9b3c522bb90816"
        }

    """
    uploaded_file = flask.request.files['file']
    stage = flask.request.form.get('stage')

    flask.current_app.logger.info(
        'Package Upload: Saving package objects to database...')
    package = new_uploaded_package(uploaded_file, stage)

    flask.current_app.logger.info(
        'Package Upload: Moving from staging to static (Public)...')
    move_staging_to_static(package.filename)

    send_new_package_command.delay(package.id)

    return flask.jsonify(
        {'filename': package.filename, 'sha1': package.sha1}), 201
