"""Custom defined Exceptions."""


class ODSException(Exception):
    """Base ODS Exception"""


class DuplicateRegisteredODS(ODSException):
    """The administrator entered an already existing remote ODS ISS"""


class ODSAuthenticationError(ODSException):
    """An authentication attempt to the ODS API failed."""


class RemoteRegistrationFailed(ODSException):
    """Registration with another ODS has failed."""
