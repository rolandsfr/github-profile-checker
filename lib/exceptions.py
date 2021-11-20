class Error(Exception):
    """Base class for other exceptions"""
    pass


class AuthorizationError(Error):
    """Raised when cli fails to authorize the user through the GitHub OAuth"""
    pass
