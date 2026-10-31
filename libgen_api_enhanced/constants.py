from types import MappingProxyType

from ._version import __version__

USER_AGENT = f"libgen-api-enhanced/{__version__} (+https://github.com/onurhanak/libgen-api-enhanced)"
# Read-only: requests.get(..., headers=DEFAULT_HEADERS) shares this one object across calls.
DEFAULT_HEADERS = MappingProxyType({"User-Agent": USER_AGENT})


def request_headers(headers=None):
    """DEFAULT_HEADERS with the caller's headers on top, as a new dict for each request."""
    return {**DEFAULT_HEADERS, **(headers or {})}
