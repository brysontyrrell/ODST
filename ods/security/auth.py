from datetime import datetime
import functools
import jwt

from flask import abort, current_app, g, request

from ..exc import ODSAuthenticationError
from ..database.api import get_server_data, lookup_registered_ods


def _validate_jwt(lookup=True):
    """Validate the authenticating JWT."""
    # Authorization method must be 'Bearer'
    try:
        schema, signed_token = request.headers.get('Authorization').split()
    except (AttributeError, IndexError, ValueError) as err:
        current_app.logger.exception(err)
        current_app.logger.debug('Header error')
        abort(401)
    else:
        if schema != 'Bearer':
            current_app.logger.debug('Not Bearer')
            abort(401)

    # Obtain the ISS and key of this JDS to validate the token
    ods = get_server_data()

    # Attempt to decode the token
    try:
        decoded_token = jwt.decode(
            signed_token, ods.key, algorithm='HS256', audience=ods.iss)
    except (jwt.InvalidAudienceError,
            jwt.exceptions.DecodeError,
            jwt.ExpiredSignatureError) as err:
        current_app.logger.error('JWT Validation Error: {}'.format(err))
        raise ODSAuthenticationError

    # Verify the 'iss' and 'iat'  claims have been provided
    if not all(key in decoded_token.keys() for key in ('aud', 'iss', 'iat')):
        current_app.logger.debug('Claims error')
        abort(401)

    # Verify the 'iat' is within 5 seconds (+/-) of current time.
    try:
        now = datetime.utcnow()
        token_date = datetime.utcfromtimestamp(float(decoded_token['iat']))
        if not 5 > (token_date - now).total_seconds() > -5:
            current_app.logger.debug('Time error')
            abort(401)
    except TypeError:
        current_app.logger.debug('Time error 2')
        abort(401)

    # Verify the 'aud' value matches this JDS's ISS
    if ods.iss != decoded_token['aud']:
        current_app.logger.error('Invalid audience ID')
        abort(401)

    ods = lookup_registered_ods(decoded_token['iss'])

    # If a lookup is required, abort if the authenticating JDS is not registered.
    if lookup and not ods:
        current_app.logger.debug('Lookup error')
        abort(401)

    return decoded_token, ods


def ods_auth_required(function=None, fail_on_lookup=True):
    """Require authentication on an endpoint."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token, ods = _validate_jwt(lookup=fail_on_lookup)
            g.ods_object = ods
            g.auth_token = token

            return func(*args, **kwargs)
        return wrapper
    return decorator(function) if function else decorator
