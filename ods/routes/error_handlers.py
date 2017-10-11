import flask

from ..database import db
from ..exc import (
    DuplicateRegisteredODS, ODSAuthenticationError, RemoteRegistrationFailed
)

blueprint = flask.Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(Exception)
def server_error(err):
    flask.flash('An unknown error was encountered. Check the application logs '
                'for more information.')
    flask.current_app.logger.exception(
        'An unknown server error was encountered: {}'.format(
            type(err).__name__))

    return flask.jsonify({'error': 'Unknown error: see application logs'}), 500


@blueprint.app_errorhandler(DuplicateRegisteredODS)
def duplicate_entry_in_database(err):
    db.session.rollback()
    flask.flash('The provided ISS matches a registered ODS. Check the ISS '
                'against the Registered ODS list.')
    flask.current_app.logger.exception(
        'Duplicate entry in the database not allowed.')
    return flask.jsonify({}), 409


@blueprint.app_errorhandler(RemoteRegistrationFailed)
def remote_registration_failure(err):
    db.session.rollback()
    flask.flash('Registration to the remote ODS failed. Check the URL, ISS, '
                'and key provided and try again.')
    flask.current_app.logger.exception('Remote ODS registration failed.')
    return flask.jsonify(), 400


@blueprint.app_errorhandler(ODSAuthenticationError)
def ods_api_auth_failure(err):
    flask.flash('Authentication to the remote ODS failed. Check the ISS and '
                'key provided and try again.')
    flask.current_app.logger.exception('ODS API authentication failed.')
    return flask.jsonify(), 401
