import glob
import os
import shutil

import flask
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

BUFFER_SIZE = 1024 * 1024  # 1 megabyte = 1048576


def read_in_chunks(file_object):
    """Lazy function (generator) to read a file piece by piece."""
    while True:
        data = file_object.read(BUFFER_SIZE)
        if not data:
            break

        yield data


def simple_sha1_hash(data):
    """Returns a SHA1 hash for the provided data using cryptography.io"""
    digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
    digest.update(data)
    return digest.finalize().encode('hex')


def file_sha1_hash(file_path):
    """Obtain the SHA1 hash of a file."""
    digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
    with open(file_path, 'rb') as fobj:
        while True:
            data = fobj.read(BUFFER_SIZE)
            if not data:
                break

            digest.update(data)

    return digest.finalize().encode('hex')


def file_chunk_sha1_hashes(file_path):
    """Returns a list of all SHA1 hashes for all chunks of a file."""
    sha1_hashes = list()
    with open(file_path, 'rb') as fobj:
        for chunk in read_in_chunks(fobj):
            sha1_hashes.append(simple_sha1_hash(chunk))

    return sha1_hashes


def move_staging_to_static(filename):
    staging_path = os.path.join(
        flask.current_app.config['UPLOAD_STAGING_DIR'], filename)

    static_path = os.path.join(flask.current_app.config['SHARE_DIR'], filename)

    shutil.move(staging_path, static_path)


def write_combined_file(filename, chunk_dir):
    """Write a recombined file from its chunks inside a source directory."""
    staging_path = os.path.join(
        flask.current_app.config['UPLOAD_STAGING_DIR'], filename)

    with open(staging_path, 'wb') as fobj:
        for chunk in sorted(glob.glob(os.path.join(chunk_dir, '*.chunk'))):
            with open(chunk, 'rb') as chunk_fobj:
                fobj.write(chunk_fobj.read())


def remove_staging_files(chunk_dir):
    shutil.rmtree(chunk_dir)
