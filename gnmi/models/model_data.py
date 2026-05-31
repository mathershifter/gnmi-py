# -*- coding: utf-8 -*-

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
    def decode(cls, v: pb.ModelData) -> "ModelData":
        return cls(
            name=v.name,
            organization=v.organization,
            version=v.version
        )

