# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import enum

from gnmi.util import contstantize

class Encoding(enum.Enum):
    JSON = 0
    BYTES = 1
    PROTO = 2
    ASCII = 3
    JSON_IETF = 4

    @classmethod
    def from_str(cls, v: str) -> "Encoding":
        return cls[contstantize(v)]