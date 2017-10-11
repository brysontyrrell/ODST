import os

# If there is a value set for the ODS_CONF env var it will set this to True.
# Then in factory.py the app.config.from_envvar() method will use the actual
# value to read in the user config.
ODS_CONF = True if os.getenv('ODS_CONF') else False

DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_KEY = os.getenv('DATABASE_KEY')

APP_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(APP_DIR, 'static')
SHARE_DIR = os.path.join(STATIC_DIR, 'share')

UPLOAD_STAGING_DIR = os.getenv('UPLOAD_STAGING_DIR')
QUARANTINE_DIR = ''  # Not implemented

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_BACKEND_URL = os.getenv('CELERY_BACKEND_URL', CELERY_BROKER_URL)

IS_CELERY_WORKER = False

SQLALCHEMY_TRACK_MODIFICATIONS = False

MYSQL_SERVER = os.getenv('MYSQL_SERVER')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

if MYSQL_SERVER and MYSQL_DATABASE and MYSQL_USER and MYSQL_PASSWORD:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(
        MYSQL_USER,
        MYSQL_PASSWORD,
        MYSQL_SERVER,
        MYSQL_DATABASE
    )
else:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'sqlite:////{}'.format(os.path.join(APP_DIR, 'jds-local.db')))
