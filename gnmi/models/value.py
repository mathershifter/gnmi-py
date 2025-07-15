# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import enum

import json
import typing as t
from decimal import Decimal

from google.protobuf import any_pb2

from gnmi.proto import gnmi_pb2 as pb
from dataclasses import dataclass, field

from gnmi.decorator import deprecated
from gnmi.models.model import BaseModel
from gnmi.models.encoding import Encoding
from gnmi.util import contstantize, get_gnmi_constant

T = t.TypeVar("T")

@deprecated(
    "deprecated, use double_val"
)
@dataclass
class Decimal64(BaseModel[pb.Decimal64]):
    dec: Decimal
    _dec: Decimal = field(init=False, repr=False)

    @property
    def digits(self) -> int:
        return int(float(self.dec) / 10 ** self.dec.as_tuple().exponent)

    @property
    def precision(self) -> int:
        return self.exponent * -1

    @property
    def exponent(self) -> int:
        exp = self.dec.as_tuple().exponent
        if not isinstance(exp, int):
            raise ValueError("not handling 'inf' or 'nan' exponents")

        return int(self.dec.as_tuple().exponent)

    @property
    def dec(self) -> Decimal:
        return self._dec

    @dec.setter
    def dec(self, value: t.Union[int, float, str, tuple, Decimal]):
        if isinstance(value, (str, int, tuple, Decimal)):
            self._dec = Decimal(value)
        elif isinstance(value, float):
            self._dec = Decimal(str(value))
        else:
            raise TypeError(f"Invalid type {type(value)}")

    def __float__(self) -> float:
        return float(self.dec)

    def __str__(self) -> str:
        return str(self.dec)

    def encode(self) -> pb.Decimal64:
        return pb.Decimal64(digits=self.digits, precision=self.precision)

    @classmethod
    def decode(cls, d: pb.Decimal64) -> "Decimal64":
        return cls(d.digits / 10**d.precision)

    def decimal(self) -> Decimal:
        return Decimal(str(float(self)))

class ValueType(enum.Enum):
    ANY_VAL = enum.auto()
    ASCII_VAL = enum.auto()
    BOOL_VAL = enum.auto()
    BYTES_VAL = enum.auto()
    DOUBLE_VAL = enum.auto()
    DECIMAL_VAL = enum.auto()
    FLOAT_VAL = enum.auto()
    INT_VAL = enum.auto()
    JSON_IETF_VAL = enum.auto()
    JSON_VAL = enum.auto()
    LEAFLIST_VAL = enum.auto()
    STRING_VAL = enum.auto()
    UINT_VAL = enum.auto()
    PROTO_BYTES = enum.auto()

    @classmethod
    def from_val(cls, v: T) -> "ValueType":
        if isinstance(v, str):
            return ValueType.STRING_VAL
        if isinstance(v, int):
            return ValueType.INT_VAL
        if isinstance(v, float):
            return ValueType.FLOAT_VAL
        if isinstance(v, Decimal):
            return ValueType.DECIMAL_VAL
        if isinstance(v, bool):
            return ValueType.BOOL_VAL
        if isinstance(v, bytes):
            return ValueType.BYTES_VAL
        if isinstance(v, list):
            return ValueType.LEAFLIST_VAL

        if isinstance(v, dict):
            return ValueType.JSON_VAL

        return ValueType.ANY_VAL

    def to_type(self) -> type[t.Union[Decimal64, bytes, bool, str, int, float, list]]:
        m = {
            "ANY_VAL": bytes,
            "ASCII_VAL": str,
            "BOOL_VAL": bool,
            "BYTES_VAL": bytes,
            "DECIMAL_VAL": Decimal64,
            "DOUBLE_VAL": float,
            "FLOAT_VAL": float,
            "INT_VAL": int,
            "JSON_IETF_VAL": bytes,
            "JSON_VAL": bytes,
            "LEAFLIST_VAL": list,
            "STRING_VAL": str,
            "UINT_VAL": int,
            "PROTO_BYTES": bytes,
        }
        return m[self.name]

    @classmethod
    def from_str(cls, s: str) -> "ValueType":
        return cls[contstantize(s)]

@dataclass
class Value(t.Generic[T], BaseModel[pb.Value]):
    val: T
    val_type: ValueType

    @property
    def value(self) -> T:
        return self.val

    def __str__(self) -> str:
        return str(self.val)

    def encode(self) -> pb.TypedValue:
        params = {}
        val_type = self.val_type
        # value = self.val
        if not val_type:
            val_type = ValueType.from_val(self.val)

        if val_type == ValueType.ANY_VAL:
            v = str(self.val).encode()
            params["any_val"] = any_pb2.Any(value=v)
        elif val_type == ValueType.JSON_VAL:
            params["json_val"] = json.dumps(self.val, cls=ValueJsonEncoder).encode("utf-8")
        elif val_type == ValueType.LEAFLIST_VAL:
            sl = []
            for v in list(self.val):
                sl.append(v.encode())
            params["leaflist_val"] = pb.ScalarArray(element=sl)
        elif val_type == ValueType.DECIMAL_VAL:
            params["decimal_val"] = self.val.encode()
        else:
            params[self.val_type.name.lower()] = self.val

        return pb.TypedValue(**params)

    @classmethod
    def decode(cls, tv: pb.TypedValue) -> "Value":
        if tv.HasField("any_val"):
            return Value(tv.any_val, ValueType.ANY_VAL)
        elif tv.HasField("ascii_val"):
            return Value(tv.ascii_val, ValueType.ASCII_VAL)
        elif tv.HasField("bool_val"):
            return Value(tv.bool_val, ValueType.BOOL_VAL)
        elif tv.HasField("bytes_val"):
            return Value(tv.bytes_val, ValueType.BYTES_VAL)
        elif tv.HasField("decimal_val"):
            val = Decimal(tv.decimal_val.digits / 10**tv.decimal_val.precision)
            return Value(val, ValueType.DECIMAL_VAL)
        elif tv.HasField("double_val"):
            return Value(tv.double_val, ValueType.DOUBLE_VAL)
        elif tv.HasField("float_val"):
            return Value(tv.float_val, ValueType.FLOAT_VAL)
        elif tv.HasField("int_val"):
            return Value(tv.int_val, ValueType.INT_VAL)
        elif tv.HasField("json_ietf_val"):
            return Value(json.loads(tv.json_ietf_val), ValueType.JSON_IETF_VAL)
        elif tv.HasField("json_val"):
            return Value(json.loads(tv.json_val), ValueType.JSON_VAL)
        elif tv.HasField("leaflist_val"):
            val = []
            for elem in tv.leaflist_val.element:
                val.append(cls.decode(elem))
            return Value(val, ValueType.LEAFLIST_VAL)
        elif tv.HasField("proto_bytes"):
            return Value(tv.proto_bytes, ValueType.PROTO_BYTES)
        elif tv.HasField("string_val"):
            return Value(tv.string_val, ValueType.STRING_VAL)
        elif tv.HasField("uint_val"):
            return Value(tv.uint_val, ValueType.UINT_VAL)
        else:
            raise ValueError("Unhandled typed value %s" % tv)

class ValueJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Value):
            return o.value
        return o

class ValueDescriptor:
    def __init__(self, *, default: None):
        self._default = default

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self._default

        return getattr(instance, self.name, self._default)

    def __set__(self, instance, value):
        setattr(instance, self.name, value_factory(value))

def value_type_factory(typ: t.Union[ValueType, str]) -> ValueType:
    if isinstance(typ, ValueType):
        return typ
    elif isinstance(typ, str):
       return ValueType.from_str(typ)
    else:
        raise ValueError("Unhandled typed value %s" % typ)

def value_factory(v) -> Value:
    if isinstance(v, Value):
        return v
    elif isinstance(v, pb.TypedValue):
        return Value.decode(v)
    elif isinstance(v, tuple):
        if len(v) == 2:
            val, typ = v
            return Value(val, value_type_factory(typ))
    else:
        # guess we'll have to guess
        return Value(v, ValueType.from_val(v))

    raise ValueError("Unhandled value %s" % v)

@dataclass
class LegacyValue(BaseModel[pb.Value]):
    value: bytes
    type: Encoding
    #
    # def extract_val(self) -> t.Any:
    #     if self.type.name in ("JSON_IETF", "JSON", "BYTES", "PROTO") and self.value:
    #         return self.value
    #     elif self.type.name == "ASCII":
    #         return str(self.value)
    #     raise ValueError("Unhandled type of value %s" % str(self.value))

    def encode(self) -> pb.Value:
        return pb.Value(value=self.value, type=get_gnmi_constant(self.type.name))

    @classmethod
    def decode(cls, tv: pb.Value) -> "LegacyValue":
        return LegacyValue(tv.value, Encoding.from_str(str(tv.type)))