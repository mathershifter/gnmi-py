# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.model import BaseModel

@dataclass
class ModelData(BaseModel[pb.ModelData]):
    name: str
    organization: str
    version: str

    def encode(self) -> pb.ModelData:
        return pb.ModelData(
            name=self.name,
            organization=self.organization,
            version=self.version
        )

    @classmethod
    def decode(cls, data: pb.ModelData) -> "ModelData":
        return cls(
            name=data.name,
            organization=data.organization,
            version=data.version
        )

