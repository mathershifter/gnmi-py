# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from typing import Any, Sequence, TypeVar

from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, PathDescriptor, path_factory
from gnmi.models.value import ValueDescriptor, value_factory

T = TypeVar('T')

@dataclass
class Update(BaseModel[pb.Update]):
    path: PathDescriptor = PathDescriptor()
    value: ValueDescriptor = ValueDescriptor()
    duplicates: int = 0

    def encode(self) -> pb.Update:
        val = None
        if self.value:
            val = value_factory(self.value).encode()
        return pb.Update(
            path=self.path.encode() if self.path else None,
            val=val,
            duplicates=self.duplicates,
        )

    @classmethod
    def decode(cls, v: pb.Update) -> "Update":
        return cls(
            path=Path.decode(v.path),
            value=value_factory(v.val),
            duplicates=v.duplicates,
        )

UpdateTuple_ = tuple[str, Any] | tuple[str, Any, int]
UpdateItem_ = Update | pb.Update | UpdateTuple_
UpdateList = Sequence[UpdateItem_]


class Updates:
    def __set_name__(self, _, name):
        self._name = "_" + name
    
    def __get__(self, inst, _):
        return getattr(inst, self._name, [])


    def __set__(self, inst, value: UpdateList):
        if not value:
            return []
        setattr(inst, self._name, update_list_factory(value))

def update_list_factory(ul: UpdateList) -> list[Update]:
    if not isinstance(ul, list):
        return []

    return [update_factory(update) for update in ul]


def update_factory(update: UpdateItem_) -> Update:

    if isinstance(update, Update):
        return update

    if isinstance(update, pb.Update):
        return Update.decode(update)

    if isinstance(update, tuple):
        
        if len(update) >= 2:
            dups = update[2] if len(update) == 3 else 0
            path = path_factory(update[0])
            return Update(path, update[1], dups)

    raise ValueError("Invalid update format")
