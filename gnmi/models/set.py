# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import typing as t
from dataclasses import dataclass, field

from gnmi.models.path import PathDescriptor, Path, path_factory
from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.model import BaseModel
from gnmi.models.update import Update
from gnmi.models.update_result import UpdateResult
from gnmi.models.error import Error
from gnmi.models.update import update_list_factory

@dataclass
class SetRequest(BaseModel[pb.SetRequest]):
    prefix: PathDescriptor = PathDescriptor(default="")
    deletes: list[t.Union[Path, str]] = field(default_factory=list)
    replacements: list[Update] = field(default_factory=list)
    updates: list[Update] = field(default_factory=list)
    union_replacements: list[Update] = field(default_factory=list)
    extensions: list[ext_pb2.Extension] = field(default_factory=list)

    @staticmethod
    def deletes_factory(deletes: list[t.Union[str, Path]]) -> list[Path]:
        return [path_factory(d) for d in deletes]

    @staticmethod
    def updates_factory(d) -> list[Update]:
        return update_list_factory(d)

    @staticmethod
    def replacements_factory(d) -> list[Update]:
        return update_list_factory(d)

    @staticmethod
    def union_replacements_factory(d) -> list[Update]:
        return update_list_factory(d)


    def encode(self) -> pb.SetRequest:
        pfx: t.Optional[Path] = None

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
    def decode(cls, s: pb.SetRequest) -> "SetRequest":
        return cls(
            prefix=s.prefix,
            deletes=list(s.delete),
            updates=list(s.update),
            replacements=list(s.replace),
            union_replacements=list(s.union_replace),
            extensions=list(s.extension)
        )


@dataclass
class SetResponse(BaseModel[pb.SetResponse]):
    prefix: PathDescriptor = PathDescriptor(default="")
    responses: list[t.Union[UpdateResult, pb.UpdateResult]] = None
    message: Error = None
    timestamp: int = 0
    extensions: list[ext_pb2.Extension] = field(default_factory=list)

    @staticmethod
    def responses_factory(responses: list[t.Union[UpdateResult, pb.UpdateResult]]) -> list[UpdateResult]:
        rsps = []
        for r in responses:
            if isinstance(r, UpdateResult):
                rsps.append(r)
            elif isinstance(r, pb.UpdateResult):
                rsps.append(UpdateResult.decode(r))

        return rsps


    def encode(self) -> pb.SetResponse:
        return pb.SetResponse(
            prefix=self.prefix.encode(),
            message=self.message.encode(),
            response=[r.encode() for r in self.responses],
            timestamp=self.timestamp,
            extension=self.extensions
        )

    @classmethod
    def decode(cls, s: pb.SetResponse) -> "SetResponse":
        return cls(
            prefix=s.prefix,
            responses=list(s.response),
            message=Error.decode(s.message),
            timestamp=s.timestamp,
            extensions=list(s.extension),

        )