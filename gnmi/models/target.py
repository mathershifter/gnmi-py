# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from dataclasses import dataclass, field

from gnmi.models.model import BaseModel
from gnmi.proto import target_pb2 as pb

IANA_GNMI_PORT = 50051

# @dataclass
# class Address:
#     host: str
#     port: int = IANA_GNMI_PORT
#
#     @classmethod
#     def from_str(cls, addr: str) -> "Address":
#         host = "localhost"
#         port = IANA_GNMI_PORT
#
#         host_, port_ = split_addr_port(addr)
#         if host_:
#             host = host_
#
#         if port_ > 0:
#             port = port_
#
#         return cls(host, port)
#
#     @property
#     def host_port(self) -> tuple[str, int]:
#         return self.host, self.port
#
#     def __str__(self) -> str:
#         host = self.host
#         if ":" in host:
#             host = f"[{host}]"
#
#         return f"{host}:{self.port}"

@dataclass
class Target(BaseModel[pb.Target]):
    address: str
    metadata: dict[str, str] = field(default_factory=dict)

    # @staticmethod
    # def address_factory(addr: t.Union[str, Address]) -> Address:
    #
    #     if isinstance(addr, Address):
    #         return addr
    #
    #     if isinstance(addr, str):
    #         return Address.from_str(addr)
    #
    #     raise TypeError(f"Address type {type(addr)} not supported")

    def __str__(self) -> str:
        return str(self.address)

    def encode(self) -> pb.Target:
        return pb.Target(
            addresses=[self.address],
            meta=self.metadata,
        )

    @classmethod
    def decode(cls, tgt: pb.Target) -> "Target":
        return cls(
            address=tgt.addresses[0],
            metadata=dict(tgt.meta),
        )

# def split_addr_port(addr: str) -> t.Tuple[str, int]:
#     host = ""
#     port = 0
#
#     buf = ""
#
#     in_host = True
#     in_v6_host = False
#
#     for c in addr:
#
#         if c == '[':
#             in_v6_host = True
#             continue
#
#         if c == ']':
#             in_v6_host = False
#             continue
#
#         if c == ":" and not in_v6_host:
#             in_host = False
#             host = buf
#             buf = ""
#             continue
#
#         buf += c
#
#     if len(buf) > 0:
#         if in_host:
#             host = buf
#             port = 0
#         else:
#             port = int(buf)
#
#     return host, int(port)


