# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import sys

if sys.version_info < (3, 9):
    # see: https://devguide.python.org/devcycle/
    raise ValueError("Python 3.9+ is required")

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("gnmi")
except PackageNotFoundError:
    # package is not installed
    pass

from gnmi.session import Session
from gnmi.api import capabilites, delete, get, replace, subscribe, update

__all__ = ["Session", "capabilites", "delete", "get", "replace", "subscribe", "update"]
