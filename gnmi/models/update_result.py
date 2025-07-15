# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
import typing as t

from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.error import Error
from gnmi.models.path import PathDescriptor
from gnmi.util import contstantize

class Operation(enum.Enum):
    INVALID = 0
    DELETE = 1
    REPLACE = 2
    UPDATE = 3
    UNION_REPLACE = 4

    @classmethod
    def from_str(cls, v: str) -> "Operation":
        return cls[contstantize(v)]

@dataclass
class UpdateResult(BaseModel[pb.UpdateResult]):
    path: PathDescriptor = PathDescriptor(default=None)
    op: t.Union[Operation, int, str] = Operation.INVALID
    timestamp: t.Optional[int] = None
    error: t.Optional[Error] = None

    @staticmethod
    def op_factory(op: t.Union[str, int, Operation]) -> Operation:
        if isinstance(op, str):
            return Operation.from_str(op)
        elif isinstance(op, int):
            return Operation(op)
        elif isinstance(op, Operation):
            return op
        else:
            raise ValueError("Invalid operation type")


    def encode(self) -> pb.UpdateResult:
        return pb.UpdateResult(
            path=self.path.encode(),
            op=self.op.name,
        )

    @classmethod
    def decode(cls, r: pb.UpdateResult) -> "UpdateResult":
        return cls(
            path=r.path,
            op=int(r.op)
        )