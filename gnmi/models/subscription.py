# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
import typing as t

from dataclasses import dataclass

from  gnmi.models.descriptor import Duration, Enum
from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import contstantize, get_gnmi_constant
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, path_factory

class SubscriptionMode(enum.Enum):
    TARGET_DEFINED = 0
    ON_CHANGE = 1
    SAMPLE = 2

    @classmethod
    def from_str(cls, s: str) -> "SubscriptionMode":
        s = contstantize(s)

        if s == "TARGET_DEFINED":
            return cls.TARGET_DEFINED
        if s == "ON_CHANGE":
            return cls.ON_CHANGE
        if s == "SAMPLE":
            return cls.SAMPLE
        raise ValueError(f"invalid subscription mode: {s}")


@dataclass
class Subscription(BaseModel[pb.Subscription]):
    path: t.Union[pb.Path, Path, str]
    mode: Enum[SubscriptionMode] = Enum(default=SubscriptionMode.TARGET_DEFINED)
    # ns between samples in SAMPLE mode.
    sample_interval: Duration = Duration(default=0)
    # unsigned int in ns
    heartbeat_interval: Duration = Duration(default=0)
    suppress_redundant: bool = False

    @staticmethod
    def path_factory(path: t.Union[pb.Path, Path, str]) -> Path:
        return path_factory(path)

    def encode(self) -> pb.Subscription:
        submode = get_gnmi_constant(self.mode.name)
        path_ = self.path.encode()
        return pb.Subscription(
            path=path_,
            mode=submode,
            suppress_redundant=self.suppress_redundant,
            sample_interval=self.sample_interval,
            heartbeat_interval=self.heartbeat_interval,
        )

    @classmethod
    def decode(cls, s: pb.Subscription) -> "Subscription":
        return cls(
            path=s.path,
            mode=SubscriptionMode(s.mode),
            heartbeat_interval=s.heartbeat_interval,
            sample_interval=s.sample_interval,
            suppress_redundant=s.suppress_redundant,
        )