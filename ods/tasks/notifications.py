import flask

from . import celery
from ..api_clients.ods_client import ODSClient
from ..database import db
from ..database.api import all_registered_ods


@celery.task()
def send_new_package_command(package_id):
    for ods in all_registered_ods():
        flask.current_app.logger.info(
            'Package Upload: Sending new package notification to ODS: '
            '{}'.format(ods.iss))

        client = ODSClient(ods)
        client.send_command(
            {'command': 'new_package', 'package_id': package_id})

    db.session.remove()
