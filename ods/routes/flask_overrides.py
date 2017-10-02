import os

import flask
from werkzeug.utils import secure_filename

from ..database.models import Package


ALLOWED_EXTENSIONS = {'dmg', 'pkg', 'zip'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class PatchedRequest(flask.Request):
    """Override the default Flask Request object with a new _get_file_stream()
    method that will write the file directly to disk upon upload and bypass
    memory and/or other temporary file space. This addresses issues with large
    file uploads in Flask.

    Because the upload immediately begins as soon as flask.request.files is
    called in the executing code, all error and safety checks are performed here
    before the file object is returned.

    ***See if this can be implemented elsewhere in the class.***
    """
    def _get_file_stream(self, total_content_length, content_type,
                         filename=None, content_length=None):

        filename = secure_filename(filename)

        # Replace these with custom exceptions
        if filename == '':
            flask.current_app.logger.error('Package Upload: No filename found!')
            flask.abort(400)
        elif not allowed_file(filename):
            flask.current_app.logger.error(
                'Package Upload: Unsupported file type!')
            flask.abort(400)

        if Package.query.filter_by(filename=filename).all():
            flask.current_app.logger.error(
                'Package Upload: The filename already exists in the share!')
            flask.abort(409)

        upload_path = os.path.join(
            flask.current_app.config['UPLOAD_STAGING_DIR'], filename)

        return open(upload_path, 'wb')


