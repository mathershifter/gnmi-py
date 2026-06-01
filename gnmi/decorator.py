# -*- coding: utf-8 -*-

import os
import warnings
import functools

from gnmi.exceptions import GnmiDeprecationError
from gnmi._env import env

warnings.simplefilter("once", category=PendingDeprecationWarning)
warnings.simplefilter("once", category=DeprecationWarning)


def deprecated(msg, cls=DeprecationWarning):
    def decorator(target):
        if isinstance(target, type):
            orig_init = target.__init__

            @functools.wraps(orig_init)
            def __init__(self, *args, **kwargs):
                if env.GNMIP_NO_DEPRECATED:
                    raise GnmiDeprecationError(msg)
                warnings.warn(msg, cls, stacklevel=2)
                orig_init(self, *args, **kwargs)

            target.__init__ = __init__
            return target

        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            if env.GNMIP_NO_DEPRECATED:
                raise GnmiDeprecationError(msg)
            warnings.warn(msg, cls, stacklevel=2)
            return target(*args, **kwargs)

        return wrapper

    return decorator
