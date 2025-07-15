# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
import typing as t

from dataclasses import dataclass, field

from gnmi.models.path import PathDescriptor, Path, path_factory
from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.model import BaseModel
from gnmi.models.notification import Notification
from gnmi.models.error import Error

class DataType(enum.Enum):
    ALL = 0
    CONFIG = 1
    STATE = 2
    OPERATIONAL = 3

@dataclass
class GetRequest(BaseModel[pb.GetRequest]):
    prefix: PathDescriptor = PathDescriptor(default="")
    paths: list[t.Union[str,Path]] = field(default_factory=list)
    type: DataType = DataType.ALL

    @staticmethod
    def paths_factory(paths: list[t.Union[Path, str]]) -> list[Path]:

        return [path_factory(p) for p in paths]

    def encode(self) -> pb.GetRequest:
        return pb.GetRequest(
            prefix=self.prefix.encode(),
            path=[p.encode() for p in self.paths],
            type=self.type.name,
        )

    @classmethod
    def decode(cls, gr: pb.GetRequest) -> "GetRequest":
        return cls(
            prefix=gr.prefix,
            paths=list(Path.decode(p) for p in gr.path),
            type=DataType(int(gr.type)),
        )

@dataclass
class GetResponse(BaseModel[pb.GetResponse]):
    notifications: list[t.Union[Notification, pb.Notification]]
    error: Error = None
    extension: list[ext_pb2.Extension] = field(default_factory=list)

    @staticmethod
    def notifications_factory(n: list[t.Union[Notification, pb.Notification]]) -> list[Notification]:
        notifs = []
        for notif in n:
            if isinstance(notif, Notification):
                notifs.append(notif)
            elif isinstance(notif, pb.Notification):
                notifs.append(Notification.decode(notif))

        return notifs

    def encode(self) -> pb.GetResponse:
        return pb.GetResponse(
            notification=[n.encode() for n in self.notifications]
        )

    @classmethod
    def decode(cls, gr: pb.GetResponse) -> "GetResponse":
        return cls(
            notifications=list(gr.notification),
        )