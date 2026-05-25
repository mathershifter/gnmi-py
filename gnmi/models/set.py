# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from dataclasses import dataclass, field

from gnmi.models.path import Path, Paths, PathDescriptor, path_factory
from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.model import BaseModel
from gnmi.models.update import Update
from gnmi.models.update_result import UpdateResult
from gnmi.models.error import  Error
from gnmi.models.update import Updates

@dataclass
class SetRequest(BaseModel[pb.SetRequest]):
    prefix: PathDescriptor = PathDescriptor()
    deletes: Paths = field(default=Paths())
    replacements: Updates = field(default=Updates())
    updates: Updates = field(default=Updates())
    union_replacements: Updates = field(default=Updates())
    extensions: list[ext_pb2.Extension] = field(default_factory=list)



    def encode(self) -> pb.SetRequest:
        pfx = None
        upds = []
        dlts = []
        reps = []
        ureps = []

        if self.prefix is not None and not self.prefix.is_empty():
            pfx = self.prefix.encode()

        if self.updates is not None:
            upds = [u.encode() for u in self.updates]

        if self.deletes is not None:
            dlts = [d.encode() for d in self.deletes]

        if self.replacements is not None:
            reps = [d.encode() for d in self.replacements]

        if self.union_replacements is not None:
            ureps = [d.encode() for d in self.union_replacements]

        return pb.SetRequest(
            prefix=pfx,
            delete=dlts,
            update=upds,
            replace=reps,
            union_replace=ureps,
            extension=self.extensions
        )

    @classmethod
    def decode(cls, v: pb.SetRequest) -> "SetRequest":
        return cls(
            prefix=Path.decode(v.prefix),
            deletes=[Path.decode(d) for d in v.delete],
            updates=[Update.decode(u) for u in v.update],
            replacements=[Update.decode(r) for r in v.replace],
            union_replacements=[Update.decode(ur) for ur in v.union_replace],
            extensions=list(v.extension)
        )


@dataclass
class SetResponse(BaseModel[pb.SetResponse]):
    prefix: PathDescriptor = PathDescriptor()
    responses: list[UpdateResult] = field(default_factory=list)
    message: Error | None = None
    timestamp: int = 0
    extensions: list[ext_pb2.Extension] = field(default_factory=list)

    @staticmethod
    def prefix_factory(path: pb.Path | Path | str) -> Path:
        return path_factory(path)

    @staticmethod
    def responses_factory(responses: list[UpdateResult | pb.UpdateResult]) -> list[UpdateResult]:
        rsps = []
        for r in responses:
            if isinstance(r, UpdateResult):
                rsps.append(r)
            elif isinstance(r, pb.UpdateResult):
                rsps.append(UpdateResult.decode(r))

        return rsps


    def encode(self) -> pb.SetResponse:
        pfx = None
        msg = None
        rsps = []
        if self.prefix:
            pfx = self.prefix.encode()

        if self.message:
            msg = self.message.encode()

        if self.responses:
            rsps = [r.encode() for r in self.responses]

        return pb.SetResponse(
            prefix=pfx,
            message=msg,
            response=rsps,
            timestamp=self.timestamp,
            extension=self.extensions
        )

    @classmethod
    def decode(cls, v: pb.SetResponse) -> "SetResponse":
        msg = None

        if v.message.code != 0:
            msg = Error.decode(v.message)
        
        return cls(
            prefix=Path.decode(v.prefix),
            responses=[UpdateResult.decode(u) for u in v.response],
            message=msg,
            timestamp=v.timestamp,
            extensions=list(v.extension),

        )