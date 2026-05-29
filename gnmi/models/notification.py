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
    prefix: PathDescriptor = PathDescriptor(default=None)
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
        if v.HasField('prefix'):
            prefix = Path.decode(v.prefix)
        else:
            prefix = None

        return cls(
            timestamp=v.timestamp,
            prefix=prefix,
            updates=[Update.decode(u) for u in v.update],
            deletes=[Path.decode(d) for d in v.delete],
        )

    def encode(self) -> pb.Notification:
        upds = []
        dlts = []
        if self.updates is not None:
            upds = [u.encode() for u in self.updates]

        if self.deletes is not None:
            dlts = [d.encode() for d in self.deletes]
        notif = pb.Notification(
            timestamp=self.timestamp,
            update=upds,
            delete=dlts,
        )
        
        # don't set prefix at all if it is None
        if self.prefix is not None:
            notif.MergeFrom(pb.Notification(
                prefix=self.prefix.encode()
            ))

        return notif
