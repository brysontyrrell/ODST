from datetime import datetime
import urlparse
import uuid

_EPOCH = datetime(1970, 1, 1)


def generate_uuid():
    return uuid.uuid4().hex


def human_readable_bytes(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "{:3.1f} {}".format(num, x)
        num /= 1024.0
    return "{:3.1f} {}".format(num, 'TB')


def human_readable_time(seconds):
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return '{}:{:02}:{:02}'.format(hours, mins, secs)


def timestamp(dt):
    """Returns a Unix timestamp from a datetime object.

    :param datetime dt: A datetime object

    :return: Unix timestamp
    :rtype: int
    """
    return int((dt - _EPOCH).total_seconds())


def parse_url(url):
    """Normalizes a provided URL."""
    parsed_url = urlparse.urlparse(url)
    if not (parsed_url.scheme and parsed_url.netloc):
        raise ValueError(
            'Invalid URL! Include the both scheme and server domain.')

    return urlparse.urlunparse(
        (parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
