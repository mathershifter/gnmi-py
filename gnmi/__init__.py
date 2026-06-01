# -*- coding: utf-8 -*-

import sys
from importlib.metadata import version

__version__ = version("gnmi")

if sys.version_info < (3, 10):
    # see: https://devguide.python.org/devcycle/
    raise ValueError("Python 3.10+ is required")


from gnmi.session import Session, BasicAuth
from gnmi.async_session import AsyncSession
from gnmi.tls import TLSConfig, get_server_certificate
from gnmi.api import capabilities, delete, get, replace, subscribe, update
from gnmi._env import env

__all__ = [
    "env",
    "BasicAuth",
    "AsyncSession",
    "Session",
    "TLSConfig",
    "capabilities",
    "delete",
    "get",
    "replace",
    "subscribe",
    "update",
    "get_server_certificate",
]
