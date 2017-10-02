import hashlib
import os

import flask

from . import celery
from ..database import db
from ..database.models import PackageChunk
from ..database.api import lookup_registered_ods
from ..api_clients.ods_client import ODSClient


BUFFER_SIZE = 1048576


@celery.task()
def download_chunk(filename, download_dir, package_chunk_id, jds_iss):
    """"""
    package_chunk = PackageChunk.query.get(package_chunk_id)
    client = ODSClient(lookup_registered_ods(jds_iss))

    range_start = package_chunk.chunk_index * BUFFER_SIZE
    range_end = range_start + BUFFER_SIZE - 1

    flask.current_app.logger.info(
        'Chunk download range: {}-{}'.format(range_start, range_end))

    data = client.download_chunk(filename, range_start, range_end)

    chunk_dl_hash = hashlib.sha1(data).hexdigest()

    flask.current_app.logger.info(
        'Chuck {} DL SHA1: {}'.format(package_chunk.chunk_index, chunk_dl_hash))
    flask.current_app.logger.info(
        'Chunk expected SHA1: {}'.format(package_chunk.sha1))

    if chunk_dl_hash != package_chunk.sha1:
        raise Exception
    else:
        with open(os.path.join(
                download_dir,
                '{}_.chunk'.format(package_chunk.chunk_index)
        ), 'wb') as chunk_file:
            chunk_file.write(data)

        package_chunk.downloaded = True
        db.session.commit()
