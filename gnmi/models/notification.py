# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from dataclasses import dataclass, field

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, Paths, PathDescriptor, path_factory
from gnmi.models.update import Update, Updates


@dataclass
class Notification(BaseModel[pb.Notification]):
    """A timestamped batch of path updates and deletions.

    Returned by ``Get`` and ``Subscribe`` responses. Each notification
    carries a ``timestamp`` (ns since epoch), an optional ``prefix``
    applied to every contained path, and parallel ``updates`` / ``deletes``
    lists. ``atomic=True`` indicates the batch must be applied as a unit.
    """

    timestamp: int
    prefix: PathDescriptor = PathDescriptor(default="")
    deletes: Paths = field(default=Paths())
    updates: Updates = field(default=Updates())
    atomic: bool = False

    @staticmethod
    def deletes_factory(d) -> list[Path]:
        dels = []
        for path in d:
            dels.append(path_factory(path))
        return dels

    @classmethod
    def decode(cls, v: pb.Notification) -> "Notification":

        return cls(
            timestamp=v.timestamp,
            prefix=Path.decode(v.prefix),
            updates=[Update.decode(u) for u in v.update],
            deletes=[Path.decode(d) for d in v.delete],
        )

    def encode(self) -> pb.Notification:
        pfx: pb.Path | None = None
        upds = []
        dlts = []

        if self.prefix is not None and not self.prefix.is_empty():
            if self.prefix is not None:
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
