import flask
from flask.blueprints import Blueprint
from flask_login import (
    LoginManager, login_required, current_user, login_user, logout_user
)

from ..database.api import admin_login, admin_lookup

blueprint = Blueprint('web', __name__)
login_manager = LoginManager()


@blueprint.record_once
def web_on_load(state):
    login_manager.init_app(state.app)
    login_manager.login_view = ''


@blueprint.before_request
def web_before_request():
    flask.g.user = current_user


@blueprint.errorhandler(401)
def web_error_unauthorized(error):
    """401 error page"""
    flask.current_app.logger.error(error)
    flask.flash('You must log in to view this page')
    return flask.render_template('index.html'), 401


@login_manager.user_loader
def load_user(login_id):
    return admin_lookup(login_id)


@blueprint.route('/logout')
def logout():
    logout_user()
    return flask.redirect('')


@blueprint.route('/', strict_slashes=False, methods=['GET', 'POST'])
def index():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')

    username = flask.request.form['username']
    password = flask.request.form['password']

    admin_user = admin_login(username, password)

    if admin_user is None:
        flask.flash('Username or Password is invalid')
        return flask.redirect('')

    login_user(admin_user)
    return flask.redirect(flask.request.args.get('next')
                          or flask.url_for('web.admin'))


@blueprint.route('/admin')
@login_required
def admin():
    return flask.render_template('admin.html'), 200


@blueprint.route('/packages')
@login_required
def packages():
    return flask.render_template('packages.html'), 200


@blueprint.route('/network')
@login_required
def network():
    return flask.render_template('network.html'), 200


@blueprint.route('/share/<filename>')
@blueprint.route('/Packages/<filename>')
def share_download(filename):
    return flask.send_from_directory(
        flask.current_app.config['SHARE_DIR'], filename, conditional=True), 200
