import os

from flask import current_app

from ..exc import ChunkHashFailure, PackageHashFailure
from . import celery
from ..database import db
from ..database.models import Package, PackageChunk
from ..database.api import lookup_registered_ods
from ..api_clients.ods_client import ODSClient
from .. import ods_files


@celery.task()
def download_package(package_id, ods_iss):
    package = Package.query.get(package_id)
    client = ODSClient(lookup_registered_ods(ods_iss))

    package_staging_dir = os.path.join(
        current_app.config['UPLOAD_STAGING_DIR'], package.uuid)

    if not os.path.exists(package_staging_dir):
        os.mkdir(package_staging_dir)

    def get_pending_chunks():
        return PackageChunk.query.filter_by(
            package=package.id, downloaded=False).all()

    def start_download():
        for chunk in get_pending_chunks():
            range_start = chunk.chunk_index * ods_files.BUFFER_SIZE
            range_end = range_start + ods_files.BUFFER_SIZE - 1

            current_app.logger.info(
                'Chunk download range: {}-{}'.format(range_start, range_end))

            data = client.download_chunk(
                package.filename, range_start, range_end)

            chunk_dl_hash = ods_files.simple_sha1_hash(data)

            current_app.logger.info(
                'Chuck {} DL SHA1: {}'.format(chunk.chunk_index, chunk_dl_hash))
            current_app.logger.info(
                'Chunk expected SHA1: {}'.format(chunk.sha1))

            if chunk_dl_hash != chunk.sha1:
                raise ChunkHashFailure(
                    'Chunk {} failed SHA1 verification'.format(
                        chunk.chunk_index))
            else:
                with open(os.path.join(package_staging_dir, '{}.chunk'.format(
                        str(chunk.chunk_index).zfill(6))), 'wb') as chunk_file:
                    chunk_file.write(data)

                chunk.downloaded = True
                db.session.commit()

    def complete_download():
        current_app.logger.info('Package chunk downloads complete')
        current_app.logger.info('Reconstituting original package...')

        ods_files.write_combined_file(package.filename, package_staging_dir)

        if package.sha1 != ods_files.file_sha1_hash(
            os.path.join(
                current_app.config['UPLOAD_STAGING_DIR'], package.filename)):

            db.session.remove(package)
            db.session.commit()
            raise PackageHashFailure('Package {} failed SHA1 '
                                     'verification'.format(package.filename))

        current_app.logger.info('Package {} SHA1 verification '
                                'success!'.format(package.filename))
        current_app.logger.info('Moving {} to {}'.format(
            package.filename, current_app.config['SHARE_DIR']))

        ods_files.move_staging_to_static(package.filename)

        package.status = 'Public'
        db.session.commit()

    # This can be done better - will need reworked for multi-threading
    download_failures = 0
    while True:
        try:
            start_download()
        except ChunkHashFailure as err:
            current_app.logger.error(err)
            current_app.logger.warning('Restarting package chunk downloads')
            download_failures += 1
            if download_failures >= 5:
                # Auto-quarantine logic here
                current_app.logger.error('Too many chunk download failures! '
                                         'Aborting package download...')
                break
        else:
            complete_download()
            break
        finally:
            ods_files.remove_staging_files(package_staging_dir)
