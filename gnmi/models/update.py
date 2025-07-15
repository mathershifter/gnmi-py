# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t

from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, path_factory
from gnmi.models.value import ValueDescriptor

@dataclass
class Update(BaseModel[pb.Update]):
    path: t.Union[Path, pb.Path, str] = ""
    value: ValueDescriptor = ValueDescriptor(default=None)
    duplicates: int = 0

    @staticmethod
    def path_factory(path: t.Union[pb.Path, Path, str]) -> Path:
        return path_factory(path)

    def encode(self) -> pb.Update:

        return pb.Update(
            path=self.path.encode(),
            val=self.value.encode(),
            duplicates=self.duplicates,
        )

    @classmethod
    def decode(cls, u: pb.Update) -> "Update":
        return cls(
            path=u.path,
            value=u.val,
            duplicates=u.duplicates,
        )

UpdateTuple_ = t.Union[tuple[str, t.Any], tuple[str, t.Any, int]]
UpdateItem_ = t.Union[Update, pb.Update, UpdateTuple_]
UpdateList_ = t.List[UpdateItem_]


def update_list_factory(ul: UpdateList_) -> list[Update]:
    if not isinstance(ul, list):
        return []

    return [update_factory(update) for update in ul]


def update_factory(update: UpdateItem_) -> Update:

    if isinstance(update, Update):
        return update

    if isinstance(update, pb.Update):
        return Update.decode(update)

    if isinstance(update, tuple):
        if 2 <= len(update) <= 3:
            return Update(*update)
        else:
            raise ValueError("Invalid update format")
    if isinstance(update, dict):
        return Update(**update)
    else:
        raise ValueError("Invalid update format")
