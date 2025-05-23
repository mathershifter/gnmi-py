# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
gnmi.messages
~~~~~~~~~~~~~~~~

gNMI messags wrappers

"""

import base64
import collections
import functools
import itertools
import json
import re
import warnings
import enum
from datetime import datetime
from decimal import Decimal
import typing as t
import google.protobuf.message
import grpc
from abc import ABC, abstractmethod

import google.protobuf
from gnmi.environments import GNMI_NO_DEPRECATED
from gnmi.exceptions import GnmiDeprecationError
from gnmi.proto import gnmi_pb2 as pb # type: ignore

from gnmi import util

warnings.simplefilter("once", category=PendingDeprecationWarning)
warnings.simplefilter("once", category=DeprecationWarning)

def deprecated(msg, klass=DeprecationWarning):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if GNMI_NO_DEPRECATED:
                raise GnmiDeprecationError(msg)
            warnings.warn(msg, klass, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BaseMessage(ABC):

    @abstractmethod
    def pb(self) -> google.protobuf.message.Message: ...


class IterableMessage(BaseMessage):
    @abstractmethod
    def __iter__(self):
        return iter([])

    def collect(self) -> list:
        """Collect"""
        collected = []
        for item in self:
            if isinstance(item, IterableMessage):
                item = item.collect()
            collected.append(item)
        return collected


class Notification_(IterableMessage):
    r"""Represents a gnmi.Notification message"""

    def __init__(self, message: pb.Notification):
        self._pb = message

    def __iter__(self) -> t.Iterable[t.Union["Update_", "Path_"]]:
        return itertools.chain(self.update, self.delete)

    @property
    def atomic(self) -> bool:
        return self._pb.atomic

    @property
    def prefix(self) -> "Path_":
        return Path_(self._pb.prefix)

    @property
    def timestamp(self) -> int:
        return int(self._pb.timestamp)

    @property
    def time(self) -> datetime:
        return util.datetime_from_int64(self.timestamp)

    @property
    def update(self) -> t.Iterable["Update_"]:
        for u in self._pb.update:
            yield Update_(u)

    updates = update

    @property
    def delete(self) -> t.Iterable["Path_"]:
        for path in self._pb.delete:
            yield Path_(path)

    deletes = delete

    def pb(self) -> pb.Notification:
        return self._pb


class Update_(BaseMessage):
    r"""Represents a gnmi.Update message"""

    def __init__(self, message: pb.Update):
        self._pb = message

    _TYPED_VALUE_MAP = {
        bool: "bool_val",
        dict: "json_ietf_val",
        int: "int_val",
        float: "float_val",
        str: "string_val",
    }

    _TYPE_HANDLER_MAP: dict[str, t.Callable[[t.Any], t.Any]] = {
        "bool_val": lambda value: True if value else False,
        "json_ietf_val": lambda value: json.dumps(value).encode(),
        "json_val": lambda value: json.dumps(value).encode(),
        "int_val": int,
        "float_val": float,
        "string_val": str,
    }

    @property
    def path(self) -> "Path_":
        return Path_(self._pb.path)

    @property
    def val(self) -> t.Optional["TypedValue_"]:
        if self._pb.HasField("val"):
            return TypedValue_(self._pb.val)
        return None

    @property
    def value(self) -> t.Optional["Value_"]:
        if self._pb.HasField("value"):
            return Value_(self._pb.value)
        return None

    @property
    def duplicates(self) -> int:
        return int(self._pb.duplicates)

    def pb(self) -> pb.Update:
        return self._pb
      
    def get_value(self) -> t.Any: #Optional[Union["TypedValue_", "Value_"]]:
        if self.val:
            return self.val.extract_val()
        elif self.value:
            return self.value.extract_val()
        
        return None

    @classmethod
    def from_keyval(cls, keyval: tuple[str, t.Any], forced_type: str = "") -> "Update_":
        p, value = keyval

        path = Path_.from_string(p)
        typed_value = pb.TypedValue()
        type_ = forced_type

        if not forced_type:
            type_ = cls._TYPED_VALUE_MAP.get(type(value), "")
            if not type_:
                raise ValueError(f"Invalid type: {type(value)} for {value}")
        
        handler = cls._TYPE_HANDLER_MAP.get(type_)
        if handler is None:
            raise ValueError(f"no handler for type: {type_}")
        
        setattr(typed_value, type_, handler(value))

        return cls(pb.Update(path=path.pb(), val=typed_value))

class TypedValue_(BaseMessage):
    def __init__(self, message: pb.TypedValue):
        self._pb = message

    @property
    def value(self) -> t.Any:
        return self.extract_val()

    def __str__(self):
        return str(self.extract_val())

    def pb(self) -> pb.TypedValue:
        return self._pb

    def extract_val(self) -> t.Any:
        val: t.Any
        if self._pb.HasField("any_val"):
            val = self._pb.any_val
        elif self._pb.HasField("ascii_val"):
            val = self._pb.ascii_val
        elif self._pb.HasField("bool_val"):
            val = self._pb.bool_val
        elif self._pb.HasField("bytes_val"):
            val = base64.b64encode(self._pb.bytes_val)
        elif self._pb.HasField("decimal_val"):
            val_ = self._pb.decimal_val
            val = Decimal(str(val_.digits / 10**val_.precision))
        elif self._pb.HasField("float_val"):
            val = self._pb.float_val
        elif self._pb.HasField("int_val"):
            val = self._pb.int_val
        elif self._pb.HasField("json_ietf_val"):
            val = json.loads(self._pb.json_ietf_val)
        elif self._pb.HasField("json_val"):
            val = json.loads(self._pb.json_val)
        elif self._pb.HasField("leaflist_val"):
            val = []
            for elem in self._pb.leaflist_val.element:
                val.append(TypedValue_(elem).extract_val())
        elif self._pb.HasField("proto_bytes"):
            val = self._pb.proto_bytes
        elif self._pb.HasField("string_val"):
            val = self._pb.string_val
        elif self._pb.HasField("uint_val"):
            val = self._pb.uint_val
        else:
            raise ValueError("Unhandled typed value %s" % self._pb)

        return val


class Path_(IterableMessage):
    r"""Represents a gnmi.Path message"""

    def __init__(self, message: pb.Path):
        self._pb = message

    RE_ORIGIN = re.compile(r"(?:(?P<origin>[\w\-]+)?:)?(?P<path>\S+)$")

    def __str__(self):
        return self.to_string()

    def __add__(self, other: "Path_") -> "Path_":
        elems: list[pb.PathElem] = []
        elements: list[str] = []

        for elem in itertools.chain(self.elem, other.elem):
            elems.append(elem.pb())

        # fallback to deprecated element fields
        if not elems:
            for element in itertools.chain(self.element, other.element):
                elements.append(element)

        return Path_(pb.Path(elem=elems, element=elements))

    def __iter__(self):
        return self.elem

    @property
    def elem(self) -> t.Iterable["PathElem_"]:
        for elem in self._pb.elem:
            yield PathElem_(elem)

    elems = elem

    @property
    def element(self) -> t.Iterable[str]:
        for e in self._pb.element:
            warnings.warn(
                "Field 'element' has been deprecated and may be removed in the future",
                DeprecationWarning,
                stacklevel=2,
            )
            yield e

    elements = element

    @property
    def origin(self) -> str:
        return self._pb.origin

    @property
    def target(self) -> str:
        return self._pb.target

    def to_string(self) -> str:
        path = ""
        for elem in self.elem:
            path += "/" + util.escape_string(elem.name, "/")
            for key, val in elem.key.items():
                val = util.escape_string(val, "]")
                path += "[" + key + "=" + val + "]"

        if not path and self.element:
            path = "/".join(self.element)

        if self.origin:
            path = ":".join([self.origin, path])
        return path
    
    def pb(self) -> pb.Path:
        return self._pb

    @classmethod
    def from_string(cls, path: str) -> "Path_":
        if not path:
            return cls(pb.Path(origin=None, elem=[]))

        elems: list = []

        path = path.strip()
        origin = None

        match = cls.RE_ORIGIN.search(path)
        if match:
            origin = match.group("origin")
            path = match.group("path")

        for elem in util.parse_path(path):
            elems.append(pb.PathElem(name=elem["name"], key=elem["keys"]))

        return cls(pb.Path(origin=origin, elem=elems))


class PathElem_(BaseMessage):
    r"""Represents a gnmi.PathElem message"""

    def __init__(self, message: pb.PathElem):
        self._pb = message

    @property
    def key(self) -> dict[str, str]:
        if hasattr(self._pb, "key"):
            return dict(self._pb.key)
        return {}

    @property
    def name(self) -> str:
        return self._pb.name
    
    def pb(self) -> pb.PathElem:
        return self._pb


@deprecated("Message 'Value' is deprecated and may be removed in the future")
class Value_(BaseMessage):
    def __init__(self, message: pb.Value):
        self._pb = message

    @property
    def value(self) -> t.Any:
        return self.extract_val()

    @property
    def type(self) -> "Encoding_":
        return Encoding_(self._pb.type)

    def __str__(self):
        return str(self.extract_val())
    
    def pb(self) -> pb.Value:
        return self._pb
    
    def extract_val(self) -> t.Any:
        if self.type.name in ("JSON_IETF", "JSON") and self._pb.value:
            return json.loads(self._pb.value.decode("utf-8"))
        elif self.type.name in ("BYTES", "PROTO"):
            return base64.b64encode(self._pb.value)
        elif self.type.name == "ASCII":
            return str(self._pb.value)

        raise ValueError("Unhandled type of value %s" % str(self._pb.value))


class Encoding_(enum.Enum):
    JSON = 0
    BYTES = 1
    PROTO = 2
    ASCII = 3
    JSON_IETF = 4


@deprecated(
    (
        "Deprecated in favour of using the "
        "google.golang.org/genproto/googleapis/rpc/status"
        "message in the RPC response."
    )
)
class Error_(BaseMessage):
    def __init__(self, message: pb.Error):
        self._pb = message

    @property
    def code(self) -> int:
        return self._pb.code

    @property
    def message(self) -> str:
        return self._pb.message

    @property
    def data(self) -> t.Any:
        return self._pb.data
    
    def pb(self) -> pb.Error:
        return self._pb


class SubscribeResponse_(BaseMessage):
    r"""Represents a gnmi.SubscribeResponse message"""
    
    def __init__(self, message: pb.SubscribeResponse):
        self._pb = message
    
    @property
    def sync_response(self) -> bool:
        return self._pb.sync_response

    @property
    def update(self) -> Notification_:
        return Notification_(self._pb.update)

    notification = update

    @property
    def error(self) -> t.Optional[Error_]:
        if self._pb.HasField("error"):
            return Error_(self._pb.error)
        return None
    
    def pb(self) -> pb.SubscribeResponse:
        return self._pb


class SetResponse_(IterableMessage):
    def __init__(self, message: pb.SetResponse):
        self._pb = message
    
    def __iter__(self):
        return self.response

    @property
    def timetamp(self) -> int:
        return self._pb.timestamp

    @property
    def time(self) -> datetime:
        return util.datetime_from_int64(self._pb.timestamp)

    @property
    def response(self):
        for resp in self._pb.response:
            yield UpdateResult_(resp)

    responses = response

    def pb(self) -> pb.SetResponse:
        return self._pb
    
    # @property
    # def error(self) -> t.Optional[Error_]:
    #     if self._pb.HasField("error"):
    #         return Error_(self._pb.error) # type: ignore
    #     return None


class UpdateResult_(BaseMessage):
    def __init__(self, message: pb.UpdateResult):
        self._pb = message

    class Operation_(enum.Enum):
        INVALID = 0
        DELETE = 1
        REPLACE = 2
        UPDATE = 3

    def __str__(self):
        return "%s %s" % (self.operation, self.path)

    @property
    def op(self) -> enum.Enum:
        return self.Operation_(self._pb.op)

    operation = op

    @property
    def path(self) -> Path_:
        return Path_(self._pb.path)

    def pb(self) -> pb.UpdateResult:
        return self._pb

    @property
    @deprecated(
        (
            "Deprecated timestamp for the UpdateResult, this field has been "
            "replaced by the timestamp within the SetResponse message, since "
            "all mutations effected by a set should be applied as a single "
            "transaction."
        )
    )
    def timestamp(self) -> int:
        return self._pb.timestamp

    # @property
    # def error(self) -> t.Optional[Error_]:
    #     if self._pb.HasField("error"):
    #         return Error_(self._pb.error)
    #     return None


class GetResponse_(IterableMessage):
    r"""Represents a gnmi.GetResponse message"""

    def __init__(self, message: pb.GetResponse):
        self._pb = message

    def __iter__(self):
        return self.notification

    @property
    def notification(self) -> t.Iterable[Notification_]:
        for notification in self._pb.notification:
            yield Notification_(notification)

    notifications = notification

    @property
    def error(self) -> t.Optional[Error_]:
        if self._pb.HasField("error"):
            return Error_(self._pb.error)
        return None
    
    def pb(self) -> pb.GetResponse:
        return self._pb

class CapabilityRequest_(BaseMessage):
    def __init__(self, ):
        self._pb: pb.CapabilityRequest = pb.CapabilityRequest()

    def pb(self) -> pb.CapabilityRequest:
        return self._pb

class CapabilityResponse_(BaseMessage):
    r"""Represents a gnmi.CapabilityResponse message"""

    def __init__(self, message: pb.CapabilityResponse):
        self._pb = message

    @property
    def supported_models(self) -> t.Iterable[dict]:
        for model in self._pb.supported_models:
            yield {
                "name": model.name,
                "organization": model.organization,
                "version": model.version,
            }

    models = supported_models

    @property
    def supported_encodings(self) -> list[Encoding_]:
        return [Encoding_(i) for i in self._pb.supported_encodings]

    encodings = supported_encodings

    @property
    def gnmi_version(self) -> str:
        return self._pb.gNMI_version

    version = gnmi_version

    def pb(self) -> pb.CapabilityResponse:
        return self._pb


class Status_(
    collections.namedtuple("Status_", ("code", "details", "trailing_metadata")),
    grpc.Status,
):
    @classmethod
    def from_call(cls, call) -> "Status_":
        return cls(call.code(), call.details(), call.trailing_metadata())
