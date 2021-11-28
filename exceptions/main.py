class Error(Exception):
    """Base class for other exceptions"""

    pass


class RateLimitError(Error):
    """Raise when the requests are aborted because of the rate limit"""

    pass
