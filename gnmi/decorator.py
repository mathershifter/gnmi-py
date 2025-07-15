# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import warnings
import functools

from gnmi.environments import GNMI_NO_DEPRECATED
from gnmi.exceptions import GnmiDeprecationError

warnings.simplefilter("once", category=PendingDeprecationWarning)
warnings.simplefilter("once", category=DeprecationWarning)

def deprecated(msg, cls=DeprecationWarning):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if GNMI_NO_DEPRECATED:
                raise GnmiDeprecationError(msg)
            warnings.warn(msg, cls, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator