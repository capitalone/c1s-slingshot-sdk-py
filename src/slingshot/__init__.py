"""Slingshot SDK for Python."""

from .__version__ import __version__
from .client import SlingshotClient

__all__ = [
    "SlingshotClient",
    "__version__",
]
