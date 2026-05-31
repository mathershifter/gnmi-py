# -*- coding: utf-8 -*-

import enum
import typing as t

from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.error import Error
from gnmi.models.path import Path, PathDescriptor
from gnmi.util import constantize

class Operation(enum.Enum):
    INVALID = 0
    DELETE = 1
    REPLACE = 2
    UPDATE = 3
    UNION_REPLACE = 4

    @classmethod
    def from_str(cls, v: str) -> "Operation":
        return cls[constantize(v)]

class OperationDescriptor:
    _default = Operation.INVALID
    def __set_name__(self, owner, name):
        self._name = "_"+name


    def __get__(self, inst, owner):
        return getattr(inst, self._name, self._default)


    def __set__(self, inst, value: int | str | Operation):
        op = self._default
        if isinstance(value, Operation):
            op = value
        elif isinstance(value, int):
            op = Operation(value)
        elif isinstance(value, str):
            op = Operation.from_str(value)
    
        setattr(inst, self._name, op)

@dataclass
class UpdateResult(BaseModel[pb.UpdateResult]):
    path: PathDescriptor = PathDescriptor()
    op: OperationDescriptor = OperationDescriptor()
    timestamp: int | None = None
    error: Error | None = None

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
            path=self.path.encode() if self.path else None,
            op=self.op.name,
        )

    @classmethod
    def decode(cls, v: pb.UpdateResult) -> "UpdateResult":
        return cls(
            path=Path.decode(v.path),
            op=Operation(int(v.op))
        )