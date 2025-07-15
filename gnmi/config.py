# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import typing as t

from importlib.util import find_spec
from collections.abc import Callable
from dataclasses import dataclass, field

from gnmi import util
from gnmi.deserialize import deserialize

YAML_SUPPORTED = False
if find_spec("yaml"):
    import yaml
    YAML_SUPPORTED = True

# TOML_SUPPORTED = False
# if importlib.util.find_spec("toml"):
#     import toml
#     TOML_SUPPORTED = True 

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
    ext: t.Any

@dataclass
class Capabilities(ConfigBase): ...
       
# class Encoding(enum.Enum):
#     JSON = 0
#     BYTES = 1
#     PROTO = 2
#     ASCII = 3
#     JSON_IETF = 4
#
#     @classmethod
#     def from_str(cls, v: str) -> "Encoding":
#         v = v.lower()
#         if v == "json":
#             return Encoding.JSON
#         if v == "bytes":
#             return Encoding.BYTES
#         if v == "proto":
#             return Encoding.PROTO
#         if v in ("ascii", "text"):
#             return Encoding.ASCII
#         if v == "json_ietf":
#             return Encoding.JSON_IETF
#
#         raise ValueError(f"invalid encoding: {v}")

@dataclass
class ModelData(ConfigBase):
    name: str
    organization: str
    version: str

# class DataType(enum.Enum):
#     ALL = 0
#     CONFIG = 1
#     STATE = 2
#     OPERATIONAL = 3
#
#     @classmethod
#     def from_str(cls, v: str) -> "DataType":
#         v = v.lower()
#         if v == "all":
#             return DataType.ALL
#         if v == "config":
#             return DataType.CONFIG
#         if v == "state":
#             return DataType.STATE
#         if v == "operational":
#             return DataType.OPERATIONAL
#
#         raise ValueError(f"invalid data_type: {v}")

@dataclass
class Get(ConfigBase):
    paths: list[str]

    prefix: str = ""
    # type: DataType = DataType.ALL
    type: str = "all"
    # encoding: Encoding = Encoding.JSON
    encoding: str = "json"
    use_models: t.Optional[list[ModelData]] = None

    # @classmethod
    # def deserialize_encoding(cls, data, **_) -> Encoding:
    #     return Encoding.from_str(data)
    
    # @classmethod
    # def deserialize_type(cls, data: str, **_) -> "DataType":
    #     return DataType.from_str(data)

ValType = t.Union[
    str,
    int,
    bool,
    bytes,
    float,
    list["ValType"],
]

# class ValueEncoding(enum.Enum):
#     AUTO = 0
#     # // String value.
#     # string string_val = 1;
#     STRING = 1
#     # // Integer value.
#     # int64 int_val = 2;
#     INT64 = 2
#     # // Unsigned integer value.
#     # uint64 uint_val = 3;
#     UINT64 = 3
#     # // Bool value.
#     # bool bool_val = 4;
#     BOOL = 4
#     # // Arbitrary byte sequence value.
#     # bytes bytes_val = 5;
#     BYTES = 5
#     # // Deprecated - use double_val.
#     # float float_val = 6 [deprecated = true];
#     FLOAT = 6
#     # // Floating point value.
#     # double double_val = 14;
#     DOUBLE = 14
#     # // Deprecated - use double_val.
#     # Decimal64 decimal_val = 7
#     #     [deprecated = true];
#     DECIMAL = 7
#     # // Mixed type scalar array value.
#     # ScalarArray leaflist_val = 8;
#     LEAFLIST = 8
#     # // protobuf.Any encoded bytes.
#     # google.protobuf.Any any_val = 9;
#     ANY = 9
#     # // JSON-encoded text.
#     # bytes json_val = 10;
#     JSON = 10
#     # // JSON-encoded text per RFC7951.
#     # bytes json_ietf_val = 11;
#     JSON_IETF = 11
#     # // Arbitrary ASCII text.
#     # string ascii_val = 12;
#     ASCII = 12
#     # // Protobuf binary encoded bytes. The message type is not included.
#     # // See the specification at
#     # // github.com/openconfig/reference/blob/master/rpc/gnmi/protobuf-vals.md
#     # // for a complete specification. [Experimental]
#     # bytes proto_bytes = 13;
#     PROTO_BYTES = 13
#
#     @classmethod
#     def from_str(cls, v: str) -> "ValueEncoding":
#         v = v.lower()
#         if v == "auto":
#             return ValueEncoding.AUTO
#         if v == "string":
#             return ValueEncoding.STRING
#         if v in ("int", "int64"):
#             return ValueEncoding.INT64
#         if v in ("uint", "uint64"):
#             return ValueEncoding.UINT64
#         if v == "bool":
#             return ValueEncoding.BOOL
#         if v == "bytes":
#             return ValueEncoding.BYTES
#         if v == "float":
#             return ValueEncoding.FLOAT
#         if v == "double":
#             return ValueEncoding.DOUBLE
#         if v == "deimal":
#             return ValueEncoding.DECIMAL
#         if v == "leaflist":
#             return ValueEncoding.LEAFLIST
#         if v == "any":
#             return ValueEncoding.ANY
#         if v == "json":
#             return ValueEncoding.JSON
#         if v == "json_ietf":
#             return ValueEncoding.JSON_IETF
#         if v == "ascii":
#             return ValueEncoding.ASCII
#         if v in ("proto_bytes", "proto"):
#             return ValueEncoding.PROTO_BYTES
#
#         raise ValueError(f"invalid value_encoding: {v}")

@dataclass
class Value(ConfigBase):

    value: ValType = 0
    # encoding: ValueEncoding = ValueEncoding.AUTO
    encoding: str = "auto"

    # @classmethod
    # def deserialize_encoding(cls, data, **_) -> ValueEncoding:
    #     return ValueEncoding.from_str(data)

@dataclass
class Update(ConfigBase):
    path: str
    val: Value
    duplicates: int = 0

@dataclass
class Set(ConfigBase):
    prefix: t.Optional[str] = None
    deletes: t.Optional[list[str]] = None
    replacements: t.Optional[list[Update]] = None
    updates: t.Optional[list[Update]] = None
    union_replacements: t.Optional[list[Update]] = None

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
    def deserialize_heartbeat(cls, dur: t.Union[str, int], **_) -> t.Optional[int]:
        if isinstance(dur, int):
            return dur
        return util.parse_duration(dur)

    @classmethod
    def deserialize_sample_interval(cls, dur: t.Optional[t.Union[str, int]], **_) -> t.Optional[int]:
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
    gnmi_version: t.Optional[str] = DEFAULT_GNMI_VERSION
    target: str = DEFAULT_TARGET
    insecure: bool = False
    tls: t.Optional[TlSConfig] = None
    debug_grpc: bool = False
    pretty: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
    extension: t.Optional[Extension] = None

    capabilities: t.Optional[Capabilities] = None
    get: t.Optional[Get] = None
    set: t.Optional[Set] = None
    subscribe: t.Optional[Subscribe] = None

    # outputs: t.Optional[map[str, Output]]


    @classmethod
    def deserialize_target(cls, tgt: t.Union[str, tuple[str, int]], **_) -> str:
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

def load(fn: Callable[..., dict[str, t.Any]], *args, **kwargs) -> Config: # t.Type[ConfigBase]:
    cnf = deserialize(Config, fn(*args, **kwargs))
    if isinstance(cnf, Config):
        return cnf
    raise ValueError("unexpected type returned from deserialize")

def yaml_loader(data: bytes) -> t.Any:
    if not YAML_SUPPORTED:
        raise ValueError("pyyaml module missing")
    return yaml.safe_load(data)

    