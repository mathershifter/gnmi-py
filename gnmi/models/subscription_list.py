# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
from dataclasses import dataclass, field

from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import contstantize, get_subscription_list_mode, get_gnmi_constant
from gnmi.models.model import BaseModel
from gnmi.models.subscription import Subscription
from gnmi.models.path import Path, PathDescriptor
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

class Subscriptions:
    _default = []

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self._default
        return getattr(instance, self.name, self._default)

    def __set__(self, instance, value):
        subs = []
        # if isinstance(value, (str, bytes)):
        #     Subscription(path=value)
        for s in value:
            if isinstance(s, Subscription):
                subs.append(s)
            if isinstance(s, (str, bytes)):
                subs.append(Subscription(path=str(s)))
        setattr(instance, self.name, subs)

@dataclass
class SubscriptionList(BaseModel[pb.SubscriptionList]):
    subscriptions: Subscriptions = field(default=Subscriptions())
    prefix: PathDescriptor = PathDescriptor()
    encoding: Enum[Encoding] = Enum(default=Encoding.JSON)
    mode: Enum[SubscriptionListMode] = Enum(default=SubscriptionListMode.STREAM)
    allow_aggregation: bool = False
    qos: int = 0
    updates_only: bool = False
    use_models: list[ModelData] | None = None

    def encode(self) -> pb.SubscriptionList:
        prefix = None
        models = None
        if self.prefix is not None:
            prefix = self.prefix.encode()
        
        if self.use_models is not None:
            models = [ModelData.encode(m) for m in self.use_models ]
        
        return pb.SubscriptionList(
            prefix=prefix,
            subscription=[s.encode() for s in self.subscriptions],
            qos=pb.QOSMarking(marking=self.qos),
            mode=get_subscription_list_mode(self.mode.name),  # self.mode.value,
            allow_aggregation=self.allow_aggregation,
            use_models=models,
            encoding=get_gnmi_constant(self.encoding.name),
            updates_only=self.updates_only,
        )

    @classmethod
    def decode(cls, v: pb.SubscriptionList) -> "SubscriptionList":
        return cls(
            prefix=Path.decode(v.prefix),
            subscriptions=[Subscription.decode(sub) for sub in v.subscription],
            qos=v.qos.marking,
            mode=SubscriptionListMode(v.mode),
            allow_aggregation=v.allow_aggregation,
            use_models=[ModelData.decode(m) for m in v.use_models],
            encoding=Encoding(v.encoding),
            updates_only=v.updates_only,
        )