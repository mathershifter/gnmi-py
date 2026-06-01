# -*- coding: utf-8 -*-

import enum
from dataclasses import dataclass, field
from typing import Sequence
from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import constantize, get_subscription_list_mode, get_gnmi_constant
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
        s = constantize(s)
        if s == "STREAM":
            return cls(cls.STREAM)
        if s == "ONCE":
            return cls(cls.ONCE)
        if s == "POLL":
            return cls(cls.POLL)
        raise ValueError(f"invalid subscription-list mode: {s}")


class Subscriptions:
    def __init__(self):
        self._default: Sequence[Subscription] = []

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return []
        return getattr(instance, self.name, [])

    def __set__(
        self, instance, value: Sequence[Subscription | pb.Subscription | Path | str]
    ):
        # dataclass(field(default=Subscriptions())) hands the descriptor
        # instance back to __set__ on default construction — leave the
        # backing attribute unset so __get__ returns the empty default.
        if value is self:
            return
        subs = []
        for s in value:
            if isinstance(s, Subscription):
                subs.append(s)
            elif isinstance(s, pb.Subscription):
                subs.append(Subscription.decode(s))
            elif isinstance(s, Path):
                subs.append(Subscription(path=s))
            elif isinstance(s, (str, bytes)):
                subs.append(Subscription(path=str(s)))
        setattr(instance, self.name, subs)


@dataclass
class SubscriptionList(BaseModel[pb.SubscriptionList]):
    """Wire payload for a Subscribe RPC.

    Bundles a list of :class:`Subscription` entries with an optional path
    prefix, an encoding, and a stream/once/poll mode. ``Session.subscribe``
    builds this internally; construct it directly only when wiring custom
    requests.
    """

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
            models = [ModelData.encode(m) for m in self.use_models]

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
            prefix=v.prefix,
            subscriptions=[sub for sub in v.subscription],
            qos=v.qos.marking,
            mode=SubscriptionListMode(v.mode),
            allow_aggregation=v.allow_aggregation,
            use_models=[ModelData.decode(m) for m in v.use_models],
            encoding=Encoding(v.encoding),
            updates_only=v.updates_only,
        )
