import flask
from celery import Celery

from . import config
from .database import db
from .tasks import celery
from .routes import api_admin, api_ods, web_admin, flask_overrides
from .startup import database_initialization, initial_setup, package_validation


def create_app():
    app = flask.Flask('ods')

    # Configure from defaults
    app.config.from_object(config)
    # Update with administrator config settings
    if app.config['ODS_CONF']:
        app.config.from_envvar('ODS_CONF')

    if not app.config['UPLOAD_STAGING_DIR']:
        import tempfile, os
        app.config['UPLOAD_STAGING_DIR'] = \
            tempfile.mkdtemp(prefix='ods-upload-')

    app.logger.info('Application Dir: {}'.format(app.config['APP_DIR']))
    app.logger.info('Static Dir: {}'.format(app.config['STATIC_DIR']))
    app.logger.info('Share Dir: {}'.format(app.config['SHARE_DIR']))
    app.logger.info('Upload/Staging Dir: {}'.format(
        app.config['UPLOAD_STAGING_DIR']))

    app.request_class = flask_overrides.PatchedRequest

    app.register_blueprint(api_admin.blueprint)
    app.register_blueprint(api_ods.blueprint)
    app.register_blueprint(web_admin.blueprint)

    db.init_app(app)
    configure_celery(celery, app)

    with app.app_context():
        database_initialization()
        initial_setup()
        package_validation()

    return app


def configure_celery(celery_, app):
    celery_.conf.update(app.config)

    TaskBase = celery_.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_.Task = ContextTask
