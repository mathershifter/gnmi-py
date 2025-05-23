# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t

Auth = tuple[str, t.Optional[str]]

class CertificateStore(t.TypedDict, total=False):
    certificate_chain: bytes
    private_key: bytes
    root_certificates: bytes


class Options(t.TypedDict, total=False):
    prefix: t.Any
    encoding: str
    extension: list


class GetOptions(Options, total=False):
    type: str
    use_models: list


class SubscribeOptions(Options, total=False):
    aggregate: bool
    heartbeat: t.Optional[int]
    interval: t.Optional[int]
    mode: str
    qos: int
    submode: str
    suppress: bool
    timeout: t.Optional[int]

class GrpcOptions(t.TypedDict, total=False):
    server_host_override: str
