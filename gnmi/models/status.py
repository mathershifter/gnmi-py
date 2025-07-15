# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t

from dataclasses import dataclass
import grpc

@dataclass
class Status:
    code: grpc.StatusCode
    details: str
    trailing_metadata: t.Any

    @classmethod
    def from_call(cls, call) -> "Status":
        return cls(call.code(), call.details(), call.trailing_metadata())