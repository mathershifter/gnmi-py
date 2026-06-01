# -*- coding: utf-8 -*-


from dataclasses import dataclass
from typing import Any
from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel
from gnmi.decorator import deprecated


@deprecated(
    (
        "Deprecated in favour of using the "
        "google.golang.org/genproto/googleapis/rpc/status"
        "message in the RPC response."
    )
)
@dataclass
class Error(BaseModel[pb.Error]):
    code: int | None = None
    message: str | None = None
    data: Any | None = None

    def encode(self) -> pb.Error:
        return pb.Error(code=self.code, message=self.message, data=self.data)

    @classmethod
    def decode(cls, v: pb.Error) -> "Error":
        return cls(code=v.code, message=v.message, data=v.data)
