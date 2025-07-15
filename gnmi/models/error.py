# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import typing as t
from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel

# @deprecated(
#     (
#         "Deprecated in favour of using the "
#         "google.golang.org/genproto/googleapis/rpc/status"
#         "message in the RPC response."
#     )
# )
@dataclass
class Error(BaseModel[pb.Error]):
    code: int
    message: str
    data: t.Any

    def encode(self) -> pb.Error:
        return pb.Error(code=self.code, message=self.message, data=self.data)

    @classmethod
    def decode(cls, err: pb.Error) -> "Error":
        return cls(code=err.code, message=err.message, data=err.data)
