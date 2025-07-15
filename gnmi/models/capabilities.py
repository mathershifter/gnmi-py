# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t

from dataclasses import dataclass
from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.model import BaseModel
from gnmi.models.encoding import Encoding
from gnmi.models.model_data import ModelData
from gnmi.util import get_gnmi_constant

@dataclass
class CapabilityRequest(BaseModel[pb.CapabilityRequest]):
    extension: list[ext_pb2.Extension]

    def encode(self) -> pb.CapabilityRequest:
        return pb.CapabilityRequest(
            extension=self.extension,
        )

    @classmethod
    def decode(cls, c: pb.CapabilityRequest) -> "CapabilityRequest":
        return CapabilityRequest(
            extension=list(c.extension),
        )

@dataclass
class CapabilityResponse(BaseModel[pb.CapabilityResponse]):
    supported_models: t.List[ModelData]
    supported_encodings: t.List[Encoding]
    gnmi_version: str

    def encode(self) -> pb.CapabilityResponse:
        return pb.CapabilityResponse(
            supported_models=[m.encode() for m in self.supported_models],
            supported_encodings=[get_gnmi_constant(e.name) for e in self.supported_encodings],
            gNMI_version=self.gnmi_version,
        )

    @classmethod
    def decode(cls, data: pb.CapabilityResponse) -> "CapabilityResponse":
        # data.supported_encodings
        return CapabilityResponse(
            supported_models=[ModelData.decode(m) for m in data.supported_models],
            supported_encodings=[Encoding(e) for e in data.supported_encodings],
            gnmi_version=data.gNMI_version
        )