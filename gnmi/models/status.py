# -*- coding: utf-8 -*-

from typing import Any
from dataclasses import dataclass
import grpc

@dataclass
class Status:
    code: grpc.StatusCode
    details: str
    trailing_metadata: Any

    @classmethod
    def from_call(cls, call) -> "Status":
        return cls(call.code(), call.details(), call.trailing_metadata())