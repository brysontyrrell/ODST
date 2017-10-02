from dicttoxml import dicttoxml
import requests


class JamfProClient(object):
    def __init__(self, url, username, password):
        self._url = url
        self._auth = (username, password)

    def _check_privileges(self):
        """Verify the authenticated admin account has all required priviliges
        for creating the distribution point and service account.
        """
        headers = {'Accept': 'application/json'}
        resp = requests.get(
            '{}/JSSResource/jssuser'.format(self._url),
            headers=headers,
            auth=self._auth)

        raise_for_status(resp)

        required_privileges = (
            'Create Accounts', 'Read Accounts',
            'Create Distribution Points', 'Read Distribution Points')

        if not all([priv in required_privileges for
                    priv in resp.json()['user']['priviliges']]):
            raise UnderPrivilegedError('The account lacks required privileges')

    def check_for_distributionpoint(self):
        resp = requests.get(
            '{}/JSSResource/distributionpoints/name/{}'.format(self._url))

    def create_distributionpoint(self):
        """"""
        data = {
            'name': 'jds2-1-somewhere.net',
            'ipAddress': 'jds2-1-somewhere.net',
            'ip_address': 'jds2-1-somewhere.net',
            'is_master': False,
            'share_name': 'jds2-1',
            'read_only_username': 'NA',
            'read_write_username': 'NA',
            'http_downloads_enabled': True,
            'http_url': 'https://jds2-1-somewhere.net',
            'context': '/download-endpoint',
            'protocol': 'https',
            'port': '443',
            'no_authentication_required': True,
            'username_password_required': False
        }
        xml = dicttoxml(data, custom_root='distribution_point', attr_type=False)

        resp = requests.post(
            '/JSSResource/distributionpoints/id/0'.format(self._url),
            auth=self._auth, headers={'Content-Type', 'text/xml'}, data=xml)

        raise_for_status(resp)

    def check_for_service_account(self):
        pass

    def create_service_account(self):
        data = {
            'privileges': {
                'jss_objects': [
                    {'privilege': 'Create Packages'},
                    {'privilege': 'Read Packages'},
                    {'privilege': 'Delete Packages'}
                ]
            }
        }
        xml = dicttoxml(data, custom_root='user', attr_type=False)

        resp = requests.post(
            '/JSSResource/packages/id/0'.format(self._url), auth=self._auth,
            headers={'Content-Type', 'text/xml'}, data=xml)

        raise_for_status(resp)

    def check_for_package(self):
        resp = requests.get('{}/JSSResource/packages/name/{}'.format(self._url))
        return resp.json()['items']

    def create_package(self):
        """"""
        data = {
            'name': 'PackageName.pkg',
            'filename': 'PackageName.pkg',
            'notes': 'Created by JDS: <JDS>'
        }
        xml = build_xml('package', data)

        resp = requests.post(
            '{}/JSSResource/packages/id/0'.format(self._url),
            auth=self._auth, headers={'Content-Type', 'text/xml'}, data=xml)

        raise_for_status(resp)


def raise_for_status(response):
    """
    :param requests.Response response:
    """
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        print('ERROR!')
        raise RequestError(error.message)


class JamfProException(Exception):
    pass


class RequestError(JamfProException):
    pass


class UnderPrivilegedError(JamfProException):
    pass
