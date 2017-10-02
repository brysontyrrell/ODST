import flask
import os

from ..database import db
from ..ods_files import file_sha1_hash, file_chunk_sha1_hashes
from .models import (
    AdminUser, JamfProData, ServerData, Package, PackageChunk, RegisteredODS
)
from ..security.cipher import AESCipher
from ..security.passwords import verify_key


def admin_login(username, password):
    """Used by Flask-Login."""
    admin_record = AdminUser.query.filter_by(username=username).first()
    if not admin_record:
        return None
    elif not verify_key(password, admin_record.password):
        return None
    else:
        return admin_record


def admin_lookup(login_id):
    return AdminUser.query.get(int(login_id))


def new_uploaded_package(uploaded_file, stage):
    upload_path = uploaded_file.stream.name
    if stage not in ('Prod', 'Test', 'Develop'):
        stage = 'Prod'

    flask.current_app.logger.info(
        "New Package: Filename: '{}' Stage: '{}'".format(
            uploaded_file.filename, stage))

    flask.current_app.logger.info('New Package: Generating SHA1 hashes...')
    file_sha1 = file_sha1_hash(upload_path)
    chunk_sha1s = file_chunk_sha1_hashes(upload_path)
    file_size = int(os.stat(upload_path).st_size)

    package = Package(sha1=file_sha1,
                      filename=uploaded_file.filename,
                      file_size=file_size,
                      stage=stage)

    db.session.add(package)
    flask.current_app.logger.info('New Package: Saving to database...')
    db.session.commit()

    for sha1 in chunk_sha1s:
        db.session.add(
            PackageChunk(sha1=sha1,
                         chunk_index=chunk_sha1s.index(sha1),
                         downloaded=True,
                         package=package.id)
        )
    flask.current_app.logger.info('New Package: Saving chunks to database...')
    db.session.commit()

    return package


def new_notified_package(package_data):
    package = Package(sha1=package_data['sha1'],
                      uuid=package_data['uuid'],
                      filename=package_data['filename'],
                      file_size=package_data['file_size'],
                      status='Downloading',
                      stage=package_data['stage'])

    db.session.add(package)
    flask.current_app.logger.info('New Package: Saving to database...')
    db.session.commit()

    for chunk in package_data['chunks']:
        db.session.add(
            PackageChunk(sha1=chunk['sha1'],
                         chunk_index=chunk['index'],
                         package=package.id)
        )
    flask.current_app.logger.info('New Package: Saving chunks to database...')
    db.session.commit()

    return package


def all_packages():
    return Package.query.all()


def one_package(name_or_id):
    try:
        query_arg = {'id': int(name_or_id)}
    except ValueError:
        query_arg = {'filename': name_or_id}

    package = Package.query.filter_by(**query_arg).all()
    if len(package) == 0 or len(package) > 1:
        flask.abort(404)

    return package[0]


def get_server_data():
    """Returns the database object for this JDS."""
    ods = ServerData.query.first()
    cipher = AESCipher()
    ods.key = cipher.decrypt(ods.key_encrypted)
    return ods


def new_registered_ods(iss_id, key, url):
    cipher = AESCipher()
    ods = RegisteredODS(iss=iss_id, key_encrypted=cipher.encrypt(key), url=url)
    db.session.add(ods)
    db.session.commit()
    ods.key = cipher.decrypt(ods.key_encrypted)
    return ods


def update_registered_ods(ods, **kwargs):
    for key in kwargs.keys():
        if key in ('name', 'url', 'stage', 'firewalled_mode'):
            setattr(ods, key, kwargs[key])

    db.session.commit()


def all_registered_ods():
    ods_list = RegisteredODS.query.all()
    cipher = AESCipher()
    for ods in ods_list:
        ods.key = cipher.decrypt(ods.key_encrypted)

    return ods_list


def lookup_registered_ods(iss):
    ods = RegisteredODS.query.filter_by(iss=iss).first()
    if ods:
        cipher = AESCipher()
        ods.key = cipher.decrypt(ods.key_encrypted)
    return ods


def get_jamfpro_credentials():
    cipher = AESCipher()
    account = JamfProData.query.first()
    username = cipher.decrypt(account.username)
    password = cipher.decrypt(account.password)
    return username, password
