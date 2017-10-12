import base64
from datetime import datetime

from . import db
from ..utilities import generate_uuid, human_readable_bytes, timestamp


class AdminUser(db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, default='admin')
    password = db.Column(db.String(128), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class ServerData(db.Model):
    ___tablename___ = 'server_data'

    id = db.Column(db.Integer, primary_key=True)
    iss = db.Column(db.String(32), default=generate_uuid)
    key_encrypted = db.Column(db.String(128), nullable=False)

    name = db.Column(db.String(128), nullable=False, default='ODS')
    url = db.Column(db.String(128), default=None)
    stage = db.Column(db.String(16), nullable=False, default='Prod')
    firewalled_mode = db.Column(db.Boolean, nullable=False, default=False)

    key = None

    @property
    def serialize(self):
        data = {
            'iss': self.iss,
            'name': self.name,
            'url': self.url,
            'stage': self.stage,
            'firewalled_mode': self.firewalled_mode
        }
        if self.key:
            data['key'] = base64.b64encode(self.key)

        return data


class JamfProData(db.Model):
    """
    Jamf Pro permissions:
    Packages: Create, Read, Delete
    """
    __tablename__ = 'jamfpro_server'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)


class RegisteredODS(db.Model):
    __tablename__ = 'registered_ods'

    id = db.Column(db.Integer, primary_key=True)
    iss = db.Column(db.String(32), unique=True, nullable=False)
    key_encrypted = db.Column(db.String(128), unique=True, nullable=False)

    name = db.Column(db.String(128), nullable=False, default='')
    url = db.Column(db.String(128), unique=True)
    stage = db.Column(db.String(16), nullable=False, default='Prod')
    firewalled_mode = db.Column(db.Boolean, nullable=False, default='False')

    registered_on = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    key = None

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'stage': self.stage,
            'firewalled_mode': self.firewalled_mode,
            'registered_on': self.registered_on.isoformat(),
            'registered_on_ts': timestamp(self.registered_on)
        }


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    uuid = db.Column(
        db.String(32), unique=True, nullable=False, default=generate_uuid)
    sha1 = db.Column(db.String(40), unique=True, nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(16), nullable=False, default='Public')
    stage = db.Column(db.String(16), nullable=False, default='Prod')

    chunks = db.relationship(
        'PackageChunk', backref='packages', lazy='joined', cascade='delete')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'created': self.created.isoformat(),
            'created_ts': timestamp(self.created),
            'uuid': self.uuid,
            'sha1': self.sha1,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_hr': human_readable_bytes(self.file_size),
            'status': self.status,
            'stage': self.stage
        }


class PackageChunk(db.Model):
    __tablename__ = 'package_chunks'

    id = db.Column(db.Integer, primary_key=True)
    sha1 = db.Column(db.String(40), unique=True, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    downloaded = db.Column(db.Boolean, nullable=False, default=False)

    package = db.Column(db.Integer, db.ForeignKey('packages.id'),
                        nullable=False)

    @property
    def serialize(self):
        return {
            'sha1': self.sha1,
            'index': self.chunk_index
        }
