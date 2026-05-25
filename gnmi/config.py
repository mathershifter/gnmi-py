# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
# import typing as t
from typing import Any
from importlib.util import find_spec
from collections.abc import Callable
from dataclasses import dataclass, field

from gnmi import util
from gnmi.deserialize import deserialize
from gnmi.models.path import PathLike


DEFAULT_GNMI_VERSION = "latest"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 50051
DEFAULT_TARGET = f"{DEFAULT_HOST}:{DEFAULT_PORT}"

@dataclass
class ConfigBase:
    def __post_init__(self):
        """Run validation any methods.
        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`
        """

@dataclass
class NotPresent(ConfigBase): ...

@dataclass
class Extension(ConfigBase):
    ext: Any

@dataclass
class Capabilities(ConfigBase): ...


@dataclass
class ModelData(ConfigBase):
    name: str
    organization: str
    version: str


@dataclass
class Get(ConfigBase):
    paths: list[PathLike]

    prefix: PathLike = ""
    type: str = "all"
    encoding: str = "json"
    use_models: list[ModelData] | None = None


ValType = str | int | bool | bytes | float | list["ValType"]


@dataclass
class Value(ConfigBase):

    value: ValType = 0
    encoding: str = "auto"


@dataclass
class Update(ConfigBase):
    path: str
    val: Value
    duplicates: int = 0

@dataclass
class Set(ConfigBase):
    prefix: str | None = None
    deletes: list[str] | None = None
    replacements: list[Update] | None = None
    updates: list[Update] | None = None
    union_replacements: list[Update] | None = None

@dataclass
class Subscription(ConfigBase):
    path: str

    mode: str = "target_defined"
    suppress_redundant: bool = False
    # ns between samples in SAMPLE mode.
    sample_interval: int = 0
    # unsigned int in ns
    heartbeat_interval: int = 0

    @classmethod
    def deserialize_heartbeat(cls, dur: str | int, **_) -> int | None:
        if isinstance(dur, int):
            return dur
        return util.parse_duration(dur)

    @classmethod
    def deserialize_sample_interval(cls, dur: str | int | None, **_) -> int | None:
        if dur is None or isinstance(dur, int):
            return dur
        return util.parse_duration(dur)


@dataclass
class Subscribe(ConfigBase):
    subscriptions: list[Subscription]
    prefix: str = ""
    qos: int = 0

    mode: str = "stream"
    use_models: list[ModelData] = field(default_factory=list)
    allow_aggregation: bool = False
    encoding: str = "json"
    updates_only: bool = False


@dataclass
class TlSConfig(ConfigBase):
    ca_cert: bytes = b""
    cert: bytes = b""
    key: bytes = b""
    get_server_certificates: bool = False

@dataclass
class Config(ConfigBase):
    gnmi_version: str | None = DEFAULT_GNMI_VERSION
    target: str = DEFAULT_TARGET
    insecure: bool = False
    tls: TlSConfig | None = None
    debug_grpc: bool = False
    pretty: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
    extension: Extension | None = None
    capabilities: Capabilities | None = None
    get: Get | None = None
    set: Set | None = None
    subscribe: Subscribe | None = None

    # outputs: t.Optional[map[str, Output]]


    @classmethod
    def deserialize_target(cls, tgt: str | tuple[str, int], **_) -> str:
        if isinstance(tgt, tuple):
            if len(tgt) != 2:
                return ":".join(tgt)
            if len(tgt) == 1:
                return f"{tgt[0]}:{DEFAULT_PORT}"

        if isinstance(tgt, str):
            if tgt == "":
                return DEFAULT_TARGET
            return tgt

        raise ValueError(f"invalid target: {tgt}")

def load(fn: Callable[..., dict[str, Any]], *args, **kwargs) -> Config: # t.Type[ConfigBase]:
    cnf = deserialize(Config, fn(*args, **kwargs))
    if isinstance(cnf, Config):
        return cnf
    raise ValueError("unexpected type returned from deserialize")

def yaml_loader(data: bytes) -> Any:
    if find_spec("yaml"):
        import yaml
        return yaml.safe_load(data)
    raise ValueError("pyyaml module missing")

    
def toml_loader(data: bytes) -> Any:
    try:
        import toml
        toml.load(data)
    except ImportError:
        raise