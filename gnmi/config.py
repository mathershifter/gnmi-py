# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import sys

from typing import Any

from pydantic import BaseModel, field_validator

from gnmi import util
from gnmi.models.path import PathLike

DEFAULT_GNMI_VERSION = "latest"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 50051
DEFAULT_TARGET = f"{DEFAULT_HOST}:{DEFAULT_PORT}"


class ConfigBase:
    def __post_init__(self):
        """Run validation any methods.
        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`
        """


class NotPresent(BaseModel): ...

class Extension(BaseModel):
    ext: Any

class Capabilities(BaseModel): ...

class ModelData(BaseModel):
    name: str
    organization: str
    version: str


class Get(BaseModel):
    paths: list[str] = []
    prefix: str = ""
    type: str = "all"
    encoding: str = "json"
    use_models: list[ModelData] = []

class Value(BaseModel):
    value: Any
    encoding: str = "auto"


class Update(BaseModel):
    path: str
    val: Value
    duplicates: int = 0


class Set(BaseModel):
    prefix: str = ""
    deletes: list[str] = []
    replacements: list[Update] = []
    updates: list[Update] = []
    union_replacements: list[Update] = []


class Subscription(BaseModel):
    path: str
    mode: str = "target_defined"
    suppress_redundant: bool = False
    # ns between samples in SAMPLE mode.
    sample_interval: int = 0
    # unsigned int in ns
    heartbeat_interval: int = 0

    @field_validator("sample_interval", mode="before")
    @classmethod
    def validate_sample_interval(cls, v: str | int | None):
        if v is None:
            return 0
        if isinstance(v, str):
            return util.parse_duration(v)
        return v or 0

    @field_validator("heartbeat_interval", mode="before")
    @classmethod
    def validate_heartbeat_interval(cls, v: str | int | None):
        if v is None:
            return 0
        if isinstance(v, str):
            return util.parse_duration(v)
        return v


class Subscribe(BaseModel):
    subscriptions: list[Subscription]
    prefix: str = ""
    qos: int = 0

    mode: str = "stream"
    use_models: list[ModelData] = []
    allow_aggregation: bool = False
    encoding: str = "json"
    updates_only: bool = False


class TlSConfig(BaseModel):
    ca_cert: bytes = b""
    cert: bytes = b""
    key: bytes = b""
    get_server_certificates: bool = False

class Config(BaseModel):
    gnmi_version: str | None = DEFAULT_GNMI_VERSION
    target: str = DEFAULT_TARGET
    insecure: bool = False
    tls: TlSConfig | None = None
    debug_grpc: bool = False
    pretty: bool = False
    metadata: dict[str, str] = {}
    extension: Extension | None = None
    capabilities: Capabilities | None = None
    get: Get | None = None
    set: Set | None = None
    subscribe: Subscribe | None = None


def load_config_file(path: str) -> Config:
    def _loader() -> dict[str, Any]:
        print(f"Loading config from {path}")
        if path.endswith(".toml"):
            import toml
            with open(path, "r") as f:

                return toml.load(f)
        elif path.endswith(".yaml") or path.endswith(".yml"):
            import yaml
            with open(path, "r") as f:
                c = yaml.safe_load(f.read())
                print(f"Loaded config: {c}")
                
                return c
        else:
            raise ValueError(f"Unsupported config file format: {path}")
    return Config(**_loader())