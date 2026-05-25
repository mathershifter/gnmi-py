# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import sys
from importlib.metadata import version

__version__ = version("gnmi")

if sys.version_info < (3, 10):
    # see: https://devguide.python.org/devcycle/
    raise ValueError("Python 3.10+ is required")


from gnmi.session import Session, TLSConfig, BasicAuth
from gnmi.api import capabilities, delete, get, replace, subscribe, update

__all__ = [
    "BasicAuth",
    "Session",
    "TLSConfig",
    "capabilities",
    "delete",
    "get",
    "replace",
    "subscribe",
    "update",
]
