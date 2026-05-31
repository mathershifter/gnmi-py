# -*- coding: utf-8 -*-

import enum

from dataclasses import dataclass

from  gnmi.models.descriptor import Duration, Enum
from gnmi.proto import gnmi_pb2 as pb

from gnmi.util import constantize, get_gnmi_constant
from gnmi.models.model import BaseModel
from gnmi.models.path import Path, PathDescriptor

class SubscriptionMode(enum.Enum):
    TARGET_DEFINED = 0
    ON_CHANGE = 1
    SAMPLE = 2

    @classmethod
    def from_str(cls, s: str) -> "SubscriptionMode":
        s = constantize(s)

        if s == "TARGET_DEFINED":
            return cls.TARGET_DEFINED
        if s == "ON_CHANGE":
            return cls.ON_CHANGE
        if s == "SAMPLE":
            return cls.SAMPLE
        raise ValueError(f"invalid subscription mode: {s}")


@dataclass
class Subscription(BaseModel[pb.Subscription]):
    """A single subscription entry within a ``SubscriptionList``.

    Pair of (path, submode). ``sample_interval`` and ``heartbeat_interval``
    are nanosecond Durations meaningful for ``SAMPLE`` / ``ON_CHANGE``
    submodes; ``suppress_redundant`` skips repeats of unchanged values.
    """

    path: PathDescriptor = PathDescriptor()
    mode: Enum[SubscriptionMode] = Enum(default=SubscriptionMode.TARGET_DEFINED)
    # ns between samples in SAMPLE mode.
    sample_interval: Duration = Duration(default=0)
    # unsigned int in ns
    heartbeat_interval: Duration = Duration(default=0)
    suppress_redundant: bool = False

    def encode(self) -> pb.Subscription:
        submode = get_gnmi_constant(self.mode.name)
        path_ = self.path.encode() if self.path else None
        return pb.Subscription(
            path=path_,
            mode=submode,
            suppress_redundant=self.suppress_redundant,
            sample_interval=self.sample_interval,
            heartbeat_interval=self.heartbeat_interval,
        )

    @classmethod
    def decode(cls, v: pb.Subscription) -> "Subscription":
        return cls(
            path=Path.decode(v.path),
            mode=SubscriptionMode(v.mode),
            heartbeat_interval=v.heartbeat_interval,
            sample_interval=v.sample_interval,
            suppress_redundant=v.suppress_redundant,
        )