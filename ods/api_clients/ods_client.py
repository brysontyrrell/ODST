import datetime
import json

import flask
import jwt
import requests

from ..exc import ODSAuthenticationError
from ..database.api import get_server_data
from ..security.cipher import AESCipher


class ODSClient(object):
    def __init__(self, ods):
        """

        :param ods: RegisteredODS object or matching object
        """
        self._url = ods.url
        self._remote_iss = ods.iss
        self._key = ods.key
        self._local_iss = get_server_data().iss

    def _token(self, register=False):
        payload = {
            'iss': self._local_iss,
            'iat': datetime.datetime.utcnow(),
            'aud': self._remote_iss
        }
        if register:
            this_ods = get_server_data()
            cipher = AESCipher(self._key)
            ods_json = json.dumps(this_ods.serialize)
            payload.update({
                'iss_data': cipher.encrypt(ods_json),
            })

        token = jwt.encode(payload, self._key, algorithm='HS256')
        return {'Authorization': 'Bearer {}'.format(token)}

    def send_command(self, alert_data):
        """
        {
            'command': 'new_package',
            'id': 1
        }
        :param dict alert_data:
        :return:
        """
        resp = requests.post('{}/api/ods/command'.format(self._url), headers=self._token(), json=alert_data)
        resp.raise_for_status()

    def all_packages(self):
        resp = requests.get('{}/api/ods/packages'.format(self._url), headers=self._token())
        return resp.json()['items']

    def get_package(self, name_or_id):
        resp = requests.get('{}/api/ods/packages/{}'.format(self._url, name_or_id), headers=self._token())
        return resp.json()

    def download_chunk(self, filename, range_start, range_end):
        headers = {'Range': 'bytes={}-{}'.format(range_start, range_end)}
        headers.update(self._token())
        resp = requests.get('{}/share/{}'.format(self._url, filename), headers=headers)
        return resp.content

    def register_with(self):
        resp = requests.post('{}/api/ods/register'.format(self._url), headers=self._token(True))
        _requests_error_status(resp)
        return

    def about(self):
        resp = requests.get('{}/api/ods/about'.format(self._url), headers=self._token())
        _requests_error_status(resp)
        return resp.json()


def _requests_error_status(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as err:
        # This needs to be expanded to cover status code specific responses
        flask.current_app.logger.exception(err)
        flask.current_app.logger.debug(
            '{}\m{}'.format(response.url, response.headers))
        raise ODSAuthenticationError
