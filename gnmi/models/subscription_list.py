# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
import typing as t

from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import contstantize, get_subscription_list_mode, get_gnmi_constant
from gnmi.models.model import BaseModel
from gnmi.models.subscription import Subscription
from gnmi.models.path import Path, path_factory
from gnmi.models.descriptor import Enum
from gnmi.models import Encoding, ModelData

class SubscriptionListMode(enum.Enum):
    STREAM = 0
    ONCE = 1
    POLL = 2

    @classmethod
    def from_str(cls, s: str) -> "SubscriptionListMode":
        s = contstantize(s)
        if s == "STREAM":
            return cls(cls.STREAM)
        if s == "ONCE":
            return cls(cls.ONCE)
        if s == "POLL":
            return cls(cls.POLL)
        raise ValueError(f"invalid subscription-list mode: {s}")

@dataclass
class SubscriptionList(BaseModel[pb.SubscriptionList]):
    subscriptions: list[Subscription]
    prefix: t.Union[pb.Path, Path, str]
    encoding: Enum[Encoding] = Enum(default=Encoding.JSON)
    mode: Enum[SubscriptionListMode] = Enum(default=SubscriptionListMode.STREAM)
    allow_aggregation: bool = False
    qos: int = 0
    updates_only: bool = False
    use_models: t.Optional[list[ModelData]] = None

    @staticmethod
    def prefix_factory(path: t.Union[pb.Path, Path, str]) -> Path:
        return path_factory(path)

    def encode(self) -> pb.SubscriptionList:
        prefix = None
        if self.prefix is not None:
            prefix = self.prefix.encode()
        return pb.SubscriptionList(
            prefix=prefix,
            subscription=[s.encode() for s in self.subscriptions],
            qos=pb.QOSMarking(marking=self.qos),
            mode=get_subscription_list_mode(self.mode.name),  # self.mode.value,
            allow_aggregation=self.allow_aggregation,
            use_models=self.use_models,
            encoding=get_gnmi_constant(self.encoding.name),
            updates_only=self.updates_only,
        )

    @classmethod
    def decode(cls, s: pb.SubscriptionList) -> "SubscriptionList":
        return cls(
            prefix=Path.decode(s.prefix),
            subscriptions=[Subscription.decode(sub) for sub in s.subscription],
            qos=s.qos.marking,
            mode=SubscriptionListMode(s.mode),
            allow_aggregation=s.allow_aggregation,
            use_models=[ModelData.decode(m) for m in s.use_models],
            encoding=Encoding(s.encoding),
            updates_only=s.updates_only,
        )