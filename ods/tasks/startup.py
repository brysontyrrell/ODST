import os

from flask import current_app

from . import celery
from ..database import db
from ..database.models import Package
from .. import ods_files


@celery.task()
def validate_packages():
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
        file_sha1 = ods_files.file_sha1_hash(file_path)
        file_chunk_sha1s = ods_files.file_chunk_sha1_hashes(file_path)

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

    current_app.logger.info('Startup: Package Validation complete.')
    db.session.remove()
