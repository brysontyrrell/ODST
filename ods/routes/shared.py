import flask

from ..database.api import all_packages, one_package, get_server_data


def packages_json():
    response = {'items': [package.serialize for package in all_packages()]}
    return flask.jsonify(response), 200


def package_json(name_or_id):
    package = one_package(name_or_id)
    response = package.serialize
    response['chunks'] = [chunk.serialize for chunk in package.chunks]
    return flask.jsonify(response), 200


def server_data():
    """Returns serialized data for this ODS as a JSON response.

    The decrypted ODS key will be included for requests made from the Admin
    API. If the request originates from the ODS API the key will be excluded.
    """
    ods = get_server_data()
    ods_data = ods.serialize
    if '/api/admin/' not in flask.request.url_rule.rule:
        ods_data.pop('key')

    return flask.jsonify(ods_data), 200
