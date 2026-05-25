# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum

from dataclasses import dataclass, field

from gnmi.models.path import Path, Paths, PathDescriptor, path_factory
from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.encoding import EncodingDescriptor
from gnmi.models.model import BaseModel
from gnmi.models.model_data import ModelData
from gnmi.models.notification import Notification
from gnmi.models.error import Error

class DataType(enum.Enum):
    ALL = 0
    CONFIG = 1
    STATE = 2
    OPERATIONAL = 3

class DataTypeDescrpitor:
    _default = DataType.ALL

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self._default

        return getattr(instance, self.name, self._default)

    def __set__(self, instance, value: str | int | DataType):
        dt = self._default
        if isinstance(value, DataType):
            dt = value
        elif isinstance(value, int):
            dt = DataType(value)
        elif isinstance(value, str):
            try:
                dt = DataType[value.upper()]
            except KeyError:
                raise TypeError(f"invalid data type: {value.upper()}")
        setattr(instance, self.name, dt)

@dataclass
class GetRequest(BaseModel[pb.GetRequest]):
    prefix: PathDescriptor = PathDescriptor()
    paths: Paths = field(default=Paths())
    type: DataTypeDescrpitor = DataTypeDescrpitor()
    encoding: EncodingDescriptor = EncodingDescriptor()
    models: list[ModelData] = field(default_factory=list)
    extensions: list[ext_pb2.Extension] = field(default_factory=list)

    def encode(self) -> pb.GetRequest:
        pfx = None
        if self.prefix and isinstance(self.prefix, Path):
            pfx = self.prefix.encode()

        return pb.GetRequest(
            prefix=pfx,
            path=[p.encode() for p in self.paths],
            type=self.type.name,
        )

    @classmethod
    def decode(cls, v: pb.GetRequest) -> "GetRequest":
        return cls(
            prefix=v.prefix,
            paths=v.path,
            type=DataType(int(v.type)),
        )

@dataclass
class GetResponse(BaseModel[pb.GetResponse]):
    notifications: list[Notification]
    error: Error | None = None
    extension: list[ext_pb2.Extension] = field(default_factory=list)

    def encode(self) -> pb.GetResponse:
        return pb.GetResponse(
            notification=[n.encode() for n in self.notifications]
        )

    @classmethod
    def decode(cls, v: pb.GetResponse) -> "GetResponse":
        return cls(
            notifications=[Notification.decode(n) for n in v.notification],
        )