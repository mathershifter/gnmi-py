# -*- coding: utf-8 -*-


import enum

from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import constantize


class Encoding(enum.Enum):
    JSON = 0
    BYTES = 1
    PROTO = 2
    ASCII = 3
    JSON_IETF = 4

    @classmethod
    def from_str(cls, v: str) -> "Encoding":
        return cls[constantize(v)]
    
    def encode(self) -> pb.Encoding:
        # return pb.Encoding.Value(self.name)
        return getattr(pb, constantize(self.name))

    @classmethod
    def decode(cls, v: pb.Encoding) -> "Encoding":
        name = pb.Encoding.Name(v)
        return cls[name]
        

class EncodingDescriptor:
    _default = Encoding.JSON

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self._default

        return getattr(instance, self.name, self._default)

    def __set__(self, instance, value: str | int | Encoding):
        enc = value
        if isinstance(value, str):
            enc = Encoding.from_str(value)
        elif isinstance(value, int):
            enc = Encoding(value)
    
        setattr(instance, self.name, enc)
