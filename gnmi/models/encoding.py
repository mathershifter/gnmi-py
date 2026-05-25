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

class EncodingDescriptor:
    _default = Encoding.JSON
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self._default

        return getattr(instance, self.name, self._default)

    def __set__(self, instance, value):
        enc = value
        if isinstance(value, str):
            enc = Encoding[value.upper()]
        elif isinstance(value, int):
            enc = Encoding(value)  
        setattr(instance, self.name, enc)