# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t
from dataclasses import dataclass, field

# from gnmi.models.descriptor import ListDescriptor
from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, path_factory
from gnmi.models.update import Update, update_list_factory


@dataclass
class Notification(BaseModel[pb.Notification]):
    timestamp: int
    prefix: t.Optional[t.Union[str, Path]] = "" #PathDescriptor = PathDescriptor(default="")
    deletes: list[t.Union[Path, pb.Path, str]] = field(default_factory=list)
    updates: list[t.Union[Update, pb.Update, tuple]] = field(default_factory=list)
    atomic: bool = False

    @staticmethod
    def prefix_factory(path: t.Union[pb.Path, Path, str]) -> Path:
        return path_factory(path)

    @staticmethod
    def updates_factory(u) -> list[Update]:
        ul = update_list_factory(u)
        return ul

    @staticmethod
    def deletes_factory(d) -> list[Path]:
        dels = []
        for path in d:
            dels.append(path_factory(path))
        return dels

    @classmethod
    def decode(cls, n: pb.Notification) -> "Notification":
        return cls(
            timestamp=n.timestamp,
            prefix=n.prefix,
            updates=list(n.update),
            deletes=list(n.delete),
        )

    def encode(self) -> pb.Notification:
        pfx: t.Optional[Path] = None
        upds = []
        dlts = []

        if self.prefix is not None and not self.prefix.is_empty():
            pfx = self.prefix.encode()

        if self.updates is not None:
            upds = [u.encode() for u in self.updates]

        if self.deletes is not None:
            dlts = [d.encode() for d in self.deletes]

        return pb.Notification(
            timestamp=self.timestamp,
            prefix=pfx,
            update=upds,
            delete=dlts,
        )
