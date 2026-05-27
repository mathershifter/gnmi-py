"""
Configuration model for gNMI client configuration.

For future use, this model may be extended to include additional configuration options such as authentication credentials, TLS settings, etc.
"""
from dataclasses import dataclass, field

from gnmi.models.model import BaseModel
from gnmi.models.target import Target
from gnmi.models.subscribe import SubscribeRequest
from gnmi.proto import target_pb2 as pb

@dataclass
class Configuration(BaseModel[pb.Configuration]):
    request: dict[str, SubscribeRequest] = field(default_factory=dict)
    target: dict[str, Target] = field(default_factory=dict)
    instance_id: str = ""
    meta: dict[str, str] = field(default_factory=dict)

    @classmethod
    def decode(cls, v: pb.Configuration) -> "Configuration":
        request = {}
        for k, val in v.request.items():
            request[k] = SubscribeRequest.decode(val)

        target = {}
        for k, val in v.target.items():
            target[k] = Target.decode(val)

        return cls(
            request=request,
            target=target,
            instance_id=v.instance_id,
            meta=dict(v.meta),
        )

    def encode(self) -> pb.Configuration:
        request = {}
        for k, val in self.request.items():
            request[k] = val.encode()

        target = {}
        for k, val in self.target.items():
            target[k] = val.encode()

        return pb.Configuration(
            request=request,
            target=target,
            instance_id=self.instance_id,
            meta=self.meta,
        )