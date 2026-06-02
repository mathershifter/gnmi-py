# -*- coding: utf-8 -*-

import ipaddress
from typing import TypeAlias
from dataclasses import dataclass, field

from gnmi.models.model import BaseModel
from gnmi.proto import target_pb2 as pb


@dataclass
class Target(BaseModel[pb.Target]):
    hostaddr: str
    port: int
    metadata: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        if self._is_ipv6():
            return f"[{self.hostaddr}]:{self.port}"
        return f"{self.hostaddr}:{self.port}"

    def encode(self) -> pb.Target:
        return pb.Target(
            addresses=[str(self)],
            meta=self.metadata,
        )

    @classmethod
    def decode(cls, v: pb.Target) -> "Target":
        hostaddr, port = _split_addr_port(v.addresses[0])
        return cls(
            hostaddr=hostaddr,
            port=port,
            metadata=dict(v.meta),
        )

    def _is_ipv6(self) -> bool:
        try:
            ip = ipaddress.ip_address(self.hostaddr)
            return ip.version == 6
        except ValueError:
            pass
        return False

    @property
    def address(self) -> str:
        if self.port != 0:
            return f"{self.hostaddr}:{self.port}"
        else:
            raise ValueError(f"Invalid target address, missing port: {self.hostaddr}")


TargetLike: TypeAlias = Target | pb.Target | str | tuple[str, int]


class TargetDescriptor:
    def __set_name__(self, _, name):
        self._name = "_" + name

    def __get__(self, obj, objtype=None) -> Target:
        return getattr(obj, self._name)

    def __set__(self, obj, value: TargetLike):
        value = target_factory(value)
        setattr(obj, self._name, value)


def target_factory(value: TargetLike) -> Target:
    if isinstance(value, Target):
        return value
    elif isinstance(value, pb.Target):
        return Target.decode(value)
    elif isinstance(value, tuple):
        return Target(hostaddr=value[0], port=value[1])
    elif isinstance(value, str):
        host, port = _split_addr_port(value)
        return Target(hostaddr=host, port=port)
    
    raise TypeError(f"Invalid target value: {value}")


def _split_addr_port(addr: str) -> tuple[str, int]:
    # This is a bit more complex than just splitting on ":", to handle IPv6 addresses.
    host = ""
    port = 0

    buf = ""

    in_host = True
    in_v6_host = False

    for c in addr:
        if c == "[":
            in_v6_host = True
            continue

        if c == "]":
            in_v6_host = False
            continue

        if c == ":" and not in_v6_host:
            in_host = False
            host = buf
            buf = ""
            continue

        buf += c

    if len(buf) > 0:
        if in_host:
            host = buf
            port = 0
        else:
            port = int(buf)

    return host, int(port)
