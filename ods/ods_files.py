import glob
import hashlib
import os
import shutil

import flask

BUF_SIZE = 1024 * 1024  # 1 megabyte = 1048576


def read_in_chunks(file_object):
    """Lazy function (generator) to read a file piece by piece."""
    while True:
        data = file_object.read(BUF_SIZE)
        if not data:
            break

        yield data


def file_sha1_hash(file_path):
    """Obtain the SHA1 hash of a file."""
    sha1_hash = hashlib.sha1()
    with open(file_path, 'rb') as fobj:
        while True:
            data = fobj.read(BUF_SIZE)
            if not data:
                break

            sha1_hash.update(data)

    return sha1_hash.hexdigest()


def file_chunk_sha1_hashes(file_path):
    """Returns a list of all SHA1 hashes for all chunks of a file."""
    sha1_hashes = list()
    with open(file_path, 'rb') as fobj:
        for chunk in read_in_chunks(fobj):
            sha1_hashes.append(hashlib.sha1(chunk).hexdigest())

    return sha1_hashes


def move_staging_to_static(filename):
    staging_path = os.path.join(
        flask.current_app.config['UPLOAD_STAGING_DIR'], filename)

    static_path = os.path.join(flask.current_app.config['SHARE_DIR'], filename)

    shutil.move(staging_path, static_path)


def write_combined_file(file_path, chunk_dir):
    """Write a recombined file from its chunks inside a source directory."""
    with open(os.path.join(file_path), 'wb') as fobj:
        for chunk in sorted(glob.glob(os.path.join(chunk_dir, '*.chunk'))):
            with open(chunk, 'rb') as chunk_fobj:
                fobj.write(chunk_fobj.read())

#
# URL = 'http://localhost:8000/RebuiltFile.pkg'
# CONTENT_LENGTH = int(requests.head(URL).headers['Content-Length'])
# CHUNK_COUNT = CONTENT_LENGTH // BUF_SIZE + (CONTENT_LENGTH % BUF_SIZE > 0)
#
# for x in range(0, CHUNK_COUNT):
#     START = BUF_SIZE * x
#     END = START + BUF_SIZE - 1
#     headers = {'Range': 'bytes={}-{}'.format(START, END)}
#     print(x, headers)
#     response = requests.get(URL, headers=headers)
#     if response.ok:
#         data = response.content
#         print('Chuck DL SHA1: {}'.format(hashlib.sha1(data).hexdigest()))
#         with open(os.path.join(
#                 CURRENT_DIR, '{}_file_dl.chunk'.format(x)), 'wb') as cf:
#             cf.write(data)
#
# with open(os.path.join(CURRENT_DIR, 'RebuiltFile_DL.pkg'), 'wb') as f:
#     for piece in sorted(glob.glob(os.path.join(CURRENT_DIR, '*_file_dl.chunk'))):
#         print(piece)
#         with open(piece, 'rb') as cf:
#             f.write(cf.read())
#
# file_hash2 = hashlib.sha1()
#
# with open(os.path.join(CURRENT_DIR, 'RebuiltFile_DL.pkg'), 'rb') as f:
#     while True:
#         data = f.read(BUF_SIZE)
#         if not data:
#             break
#         file_hash2.update(data)
#
# print("SHA1: {0}".format(file_hash2.hexdigest()))
