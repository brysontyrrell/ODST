import os
import time

from flask import current_app
from sqlalchemy.exc import InternalError, OperationalError

from .database import db
from .database.models import AdminUser, ServerData
from .security.cipher import AESCipher
from .security.passwords import derive_key
from .tasks.startup import validate_packages


def database_initialization():
    """Attempt to create the database schema. If the application is unable to
    perform the creation of the database it will reattempt every 30 seconds
    for 5 minutes until raising an Exception and stopping the application.
    """
    current_app.logger.info('Startup: Creating database schema...')
    for attempt in range(0, 30):
        try:
            db.create_all()
        # Will update as additional databases become supported
        except (InternalError, OperationalError) as err:
            db.session.close()
            current_app.logger.warning(
                'Startup: Database connection error: {}: '
                'Retrying in 10 seconds...'.format(err))
            time.sleep(10)
        else:
            return
    else:
        current_app.logger.error('Startup: Unable to connect to database!')
        raise


def initial_setup():
    current_app.logger.info('Startup: Initial Setup tasks...')
    cipher = AESCipher()

    if not AdminUser.query.first():
        current_app.logger.info(
            'Inital Setup: Creating default admin user for web UI')
        admin_user = AdminUser(password=derive_key('ods1234!'))
        db.session.add(admin_user)
        db.session.commit()
        current_app.logger.info(
            "Inital Setup: Default 'admin' user created")
        current_app.logger.warn(
            'Initial Setup: The default password must be changed!')

    if not ServerData.query.first():
        current_app.logger.info(
            'Initial Setup: Generating ISS ID and Key for ODS')

        key = os.urandom(32)
        ods = ServerData(key_encrypted=cipher.encrypt(key))

        db.session.add(ods)
        db.session.commit()

        current_app.logger.debug(
            'Initial Setup: A key has been created for this ODS.')
        current_app.logger.warn(
            'Initial Setup: The ODS URL must be set in the Admin console!')

    if not os.path.exists(current_app.config['SHARE_DIR']):
        try:
            os.makedirs(current_app.config['SHARE_DIR'], 0755)
            current_app.logger.info('Initial Setup: The share directory has '
                                    'been created.')
        except IOError:
            current_app.logger.error('Initial Setup: The share directory does '
                                     'not exist and cannot be created!')
            raise

    current_app.logger.info('Initial Setup: Complete.')


def package_validation():
    current_app.logger.info('Startup: Running package validation...')
    validate_packages.delay()
