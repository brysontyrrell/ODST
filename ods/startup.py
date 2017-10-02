import os
import random
import string
import time

from flask import current_app
from sqlalchemy.exc import OperationalError

from .database import db
from .database.models import AdminUser, ServerData, Package
from .ods_files import file_sha1_hash, file_chunk_sha1_hashes
from .security.cipher import AESCipher
from .security.passwords import derive_key


def database_initialization():
    """Attempt to create the database schema. If the application is unable to
    perform the creation of the database it will reattempt every 30 seconds
    for 5 minutes until raising an Exception and stopping the application.
    """
    current_app.logger.info('Startup: Creating database schema...')
    for attempt in range(0, 10):
        try:
            db.create_all()
        except OperationalError as err:
            current_app.logger.warning('Startup: Database connection '
                                       'unavailable. Retrying in 30 seconds...')
            current_app.logger.debug(err)
            time.sleep(30)
        else:
            return
    else:
        current_app.logger.error('Startup: Unable to connect to database!')
        raise


def generate_random_string(length=32):
    chars = ''.join([
        string.lowercase, string.uppercase, string.digits, string.punctuation])
    return ''.join(random.SystemRandom().choice(chars) for i in range(length))


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
        key = generate_random_string()
        ods = ServerData(key_encrypted=cipher.encrypt(key))
        db.session.add(ods)
        db.session.commit()

        current_app.logger.debug(
            'Initial Setup: A key has been created for this ODS:\n  ISS: {}\n'
            '  Key: {}\n\nUse this ISS and key and when registering other ODS '
            'instances.'.format(ods.iss, key))
        current_app.logger.warn(
            'Initial Setup: The ODS URL must be set in the Admin console!')

    if not os.path.exists(current_app.config['SHARE_DIR']):
        try:
            os.makedirs(current_app.config['SHARE_DIR'], 0755)
        except IOError:
            current_app.logger.error('Initial Setup: The share directory does '
                                     'not exist and cannot be created!')
            raise

    current_app.logger.info('Initial Setup: Complete.')


def package_validation():
    current_app.logger.info('Startup: Running package validation...')

    db_commit = False

    packages = Package.query.all()
    files = os.listdir(current_app.config['SHARE_DIR'])

    if files:
        current_app.logger.info(
            'Package Validation: Verifying packages in database against '
            '{}'.format(current_app.config['SHARE_DIR']))

    for file_ in files:
        if file_ not in [package.filename for package in packages]:
            current_app.logger.info(
                'Package Validation: Local file not found in database: '
                '{}'.format(file_))
            try:
                os.remove(os.path.join(
                    current_app.config['SHARE_DIR'], file_))
            except OSError as err:
                current_app.logger.exception(err)
                current_app.logger.error(
                    'Package Validation: Unable to remove the file: '
                    '{}'.format(err))
            else:
                current_app.logger.info(
                    'Package Validation: File removed.')

            files.remove(file_)

    for package in packages:
        if package.filename not in files:
            current_app.logger.info(
                'Package Validation: Package not found in local files: '
                '{}'.format(package.filename))
            current_app.logger.info(
                'Package Validation: Removed from database.')
            db.session.delete(package)
            packages.remove(package)
            db_commit = True

    if files:
        current_app.logger.info(
            'Package Validation: Verifying SHA1 hashes...')

    for file_ in files:
        file_path = os.path.join(current_app.config['SHARE_DIR'], file_)
        file_sha1 = file_sha1_hash(file_path)
        file_chunk_sha1s = file_chunk_sha1_hashes(file_path)
        for package in packages:
            if package.filename == file_:
                try:
                    assert file_sha1 == package.sha1
                    for chunk in package.chunks:
                        filehash = file_chunk_sha1s[chunk.chunk_index]
                        assert filehash == chunk.sha1
                except AssertionError:
                    current_app.logger.info(
                        'Package Validation: SHA1 hash verification for file '
                        'failed: {}'.format(file_))
                    os.remove(file_path)
                    db.session.delete(package)
                    db_commit = True
                else:
                    current_app.logger.info(
                        'Package Validation: SHA1 verification passed for '
                        'file: {}'.format(file_))

    if db_commit:
        db.session.commit()

    db.session.close()

    current_app.logger.info('Startup: Package Validation complete.')
