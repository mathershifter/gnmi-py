from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from . import gnmi_ext_pb2 as _gnmi_ext_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Encoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JSON: _ClassVar[Encoding]
    BYTES: _ClassVar[Encoding]
    PROTO: _ClassVar[Encoding]
    ASCII: _ClassVar[Encoding]
    JSON_IETF: _ClassVar[Encoding]

class SubscriptionMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TARGET_DEFINED: _ClassVar[SubscriptionMode]
    ON_CHANGE: _ClassVar[SubscriptionMode]
    SAMPLE: _ClassVar[SubscriptionMode]
JSON: Encoding
BYTES: Encoding
PROTO: Encoding
ASCII: Encoding
JSON_IETF: Encoding
TARGET_DEFINED: SubscriptionMode
ON_CHANGE: SubscriptionMode
SAMPLE: SubscriptionMode
GNMI_SERVICE_FIELD_NUMBER: _ClassVar[int]
gnmi_service: _descriptor.FieldDescriptor

class Notification(_message.Message):
    __slots__ = ("timestamp", "prefix", "update", "delete", "atomic")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    ATOMIC_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    prefix: Path
    update: _containers.RepeatedCompositeFieldContainer[Update]
    delete: _containers.RepeatedCompositeFieldContainer[Path]
    atomic: bool
    def __init__(self, timestamp: _Optional[int] = ..., prefix: _Optional[_Union[Path, _Mapping]] = ..., update: _Optional[_Iterable[_Union[Update, _Mapping]]] = ..., delete: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., atomic: bool = ...) -> None: ...

class Update(_message.Message):
    __slots__ = ("path", "value", "val", "duplicates")
    PATH_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    DUPLICATES_FIELD_NUMBER: _ClassVar[int]
    path: Path
    value: Value
    val: TypedValue
    duplicates: int
    def __init__(self, path: _Optional[_Union[Path, _Mapping]] = ..., value: _Optional[_Union[Value, _Mapping]] = ..., val: _Optional[_Union[TypedValue, _Mapping]] = ..., duplicates: _Optional[int] = ...) -> None: ...

class TypedValue(_message.Message):
    __slots__ = ("string_val", "int_val", "uint_val", "bool_val", "bytes_val", "float_val", "double_val", "decimal_val", "leaflist_val", "any_val", "json_val", "json_ietf_val", "ascii_val", "proto_bytes")
    STRING_VAL_FIELD_NUMBER: _ClassVar[int]
    INT_VAL_FIELD_NUMBER: _ClassVar[int]
    UINT_VAL_FIELD_NUMBER: _ClassVar[int]
    BOOL_VAL_FIELD_NUMBER: _ClassVar[int]
    BYTES_VAL_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VAL_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VAL_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_VAL_FIELD_NUMBER: _ClassVar[int]
    LEAFLIST_VAL_FIELD_NUMBER: _ClassVar[int]
    ANY_VAL_FIELD_NUMBER: _ClassVar[int]
    JSON_VAL_FIELD_NUMBER: _ClassVar[int]
    JSON_IETF_VAL_FIELD_NUMBER: _ClassVar[int]
    ASCII_VAL_FIELD_NUMBER: _ClassVar[int]
    PROTO_BYTES_FIELD_NUMBER: _ClassVar[int]
    string_val: str
    int_val: int
    uint_val: int
    bool_val: bool
    bytes_val: bytes
    float_val: float
    double_val: float
    decimal_val: Decimal64
    leaflist_val: ScalarArray
    any_val: _any_pb2.Any
    json_val: bytes
    json_ietf_val: bytes
    ascii_val: str
    proto_bytes: bytes
    def __init__(self, string_val: _Optional[str] = ..., int_val: _Optional[int] = ..., uint_val: _Optional[int] = ..., bool_val: bool = ..., bytes_val: _Optional[bytes] = ..., float_val: _Optional[float] = ..., double_val: _Optional[float] = ..., decimal_val: _Optional[_Union[Decimal64, _Mapping]] = ..., leaflist_val: _Optional[_Union[ScalarArray, _Mapping]] = ..., any_val: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., json_val: _Optional[bytes] = ..., json_ietf_val: _Optional[bytes] = ..., ascii_val: _Optional[str] = ..., proto_bytes: _Optional[bytes] = ...) -> None: ...

class Path(_message.Message):
    __slots__ = ("element", "origin", "elem", "target")
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ELEM_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    element: _containers.RepeatedScalarFieldContainer[str]
    origin: str
    elem: _containers.RepeatedCompositeFieldContainer[PathElem]
    target: str
    def __init__(self, element: _Optional[_Iterable[str]] = ..., origin: _Optional[str] = ..., elem: _Optional[_Iterable[_Union[PathElem, _Mapping]]] = ..., target: _Optional[str] = ...) -> None: ...

class PathElem(_message.Message):
    __slots__ = ("name", "key")
    class KeyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    name: str
    key: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., key: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("value", "type")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    type: Encoding
    def __init__(self, value: _Optional[bytes] = ..., type: _Optional[_Union[Encoding, str]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("code", "message", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    data: _any_pb2.Any
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Decimal64(_message.Message):
    __slots__ = ("digits", "precision")
    DIGITS_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    digits: int
    precision: int
    def __init__(self, digits: _Optional[int] = ..., precision: _Optional[int] = ...) -> None: ...

class ScalarArray(_message.Message):
    __slots__ = ("element",)
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    element: _containers.RepeatedCompositeFieldContainer[TypedValue]
    def __init__(self, element: _Optional[_Iterable[_Union[TypedValue, _Mapping]]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("subscribe", "poll", "extension")
    SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    POLL_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    subscribe: SubscriptionList
    poll: Poll
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, subscribe: _Optional[_Union[SubscriptionList, _Mapping]] = ..., poll: _Optional[_Union[Poll, _Mapping]] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class Poll(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SubscribeResponse(_message.Message):
    __slots__ = ("update", "sync_response", "error", "extension")
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    SYNC_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    update: Notification
    sync_response: bool
    error: Error
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, update: _Optional[_Union[Notification, _Mapping]] = ..., sync_response: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class SubscriptionList(_message.Message):
    __slots__ = ("prefix", "subscription", "qos", "mode", "allow_aggregation", "use_models", "encoding", "updates_only")
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STREAM: _ClassVar[SubscriptionList.Mode]
        ONCE: _ClassVar[SubscriptionList.Mode]
        POLL: _ClassVar[SubscriptionList.Mode]
    STREAM: SubscriptionList.Mode
    ONCE: SubscriptionList.Mode
    POLL: SubscriptionList.Mode
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    USE_MODELS_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    UPDATES_ONLY_FIELD_NUMBER: _ClassVar[int]
    prefix: Path
    subscription: _containers.RepeatedCompositeFieldContainer[Subscription]
    qos: QOSMarking
    mode: SubscriptionList.Mode
    allow_aggregation: bool
    use_models: _containers.RepeatedCompositeFieldContainer[ModelData]
    encoding: Encoding
    updates_only: bool
    def __init__(self, prefix: _Optional[_Union[Path, _Mapping]] = ..., subscription: _Optional[_Iterable[_Union[Subscription, _Mapping]]] = ..., qos: _Optional[_Union[QOSMarking, _Mapping]] = ..., mode: _Optional[_Union[SubscriptionList.Mode, str]] = ..., allow_aggregation: bool = ..., use_models: _Optional[_Iterable[_Union[ModelData, _Mapping]]] = ..., encoding: _Optional[_Union[Encoding, str]] = ..., updates_only: bool = ...) -> None: ...

class Subscription(_message.Message):
    __slots__ = ("path", "mode", "sample_interval", "suppress_redundant", "heartbeat_interval")
    PATH_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_REDUNDANT_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    path: Path
    mode: SubscriptionMode
    sample_interval: int
    suppress_redundant: bool
    heartbeat_interval: int
    def __init__(self, path: _Optional[_Union[Path, _Mapping]] = ..., mode: _Optional[_Union[SubscriptionMode, str]] = ..., sample_interval: _Optional[int] = ..., suppress_redundant: bool = ..., heartbeat_interval: _Optional[int] = ...) -> None: ...

class QOSMarking(_message.Message):
    __slots__ = ("marking",)
    MARKING_FIELD_NUMBER: _ClassVar[int]
    marking: int
    def __init__(self, marking: _Optional[int] = ...) -> None: ...

class SetRequest(_message.Message):
    __slots__ = ("prefix", "delete", "replace", "update", "union_replace", "extension")
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    REPLACE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    UNION_REPLACE_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    prefix: Path
    delete: _containers.RepeatedCompositeFieldContainer[Path]
    replace: _containers.RepeatedCompositeFieldContainer[Update]
    update: _containers.RepeatedCompositeFieldContainer[Update]
    union_replace: _containers.RepeatedCompositeFieldContainer[Update]
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, prefix: _Optional[_Union[Path, _Mapping]] = ..., delete: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., replace: _Optional[_Iterable[_Union[Update, _Mapping]]] = ..., update: _Optional[_Iterable[_Union[Update, _Mapping]]] = ..., union_replace: _Optional[_Iterable[_Union[Update, _Mapping]]] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class SetResponse(_message.Message):
    __slots__ = ("prefix", "response", "message", "timestamp", "extension")
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    prefix: Path
    response: _containers.RepeatedCompositeFieldContainer[UpdateResult]
    message: Error
    timestamp: int
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, prefix: _Optional[_Union[Path, _Mapping]] = ..., response: _Optional[_Iterable[_Union[UpdateResult, _Mapping]]] = ..., message: _Optional[_Union[Error, _Mapping]] = ..., timestamp: _Optional[int] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class UpdateResult(_message.Message):
    __slots__ = ("timestamp", "path", "message", "op")
    class Operation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INVALID: _ClassVar[UpdateResult.Operation]
        DELETE: _ClassVar[UpdateResult.Operation]
        REPLACE: _ClassVar[UpdateResult.Operation]
        UPDATE: _ClassVar[UpdateResult.Operation]
        UNION_REPLACE: _ClassVar[UpdateResult.Operation]
    INVALID: UpdateResult.Operation
    DELETE: UpdateResult.Operation
    REPLACE: UpdateResult.Operation
    UPDATE: UpdateResult.Operation
    UNION_REPLACE: UpdateResult.Operation
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    path: Path
    message: Error
    op: UpdateResult.Operation
    def __init__(self, timestamp: _Optional[int] = ..., path: _Optional[_Union[Path, _Mapping]] = ..., message: _Optional[_Union[Error, _Mapping]] = ..., op: _Optional[_Union[UpdateResult.Operation, str]] = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ("prefix", "path", "type", "encoding", "use_models", "extension")
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALL: _ClassVar[GetRequest.DataType]
        CONFIG: _ClassVar[GetRequest.DataType]
        STATE: _ClassVar[GetRequest.DataType]
        OPERATIONAL: _ClassVar[GetRequest.DataType]
    ALL: GetRequest.DataType
    CONFIG: GetRequest.DataType
    STATE: GetRequest.DataType
    OPERATIONAL: GetRequest.DataType
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    USE_MODELS_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    prefix: Path
    path: _containers.RepeatedCompositeFieldContainer[Path]
    type: GetRequest.DataType
    encoding: Encoding
    use_models: _containers.RepeatedCompositeFieldContainer[ModelData]
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, prefix: _Optional[_Union[Path, _Mapping]] = ..., path: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., type: _Optional[_Union[GetRequest.DataType, str]] = ..., encoding: _Optional[_Union[Encoding, str]] = ..., use_models: _Optional[_Iterable[_Union[ModelData, _Mapping]]] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("notification", "error", "extension")
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    notification: _containers.RepeatedCompositeFieldContainer[Notification]
    error: Error
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, notification: _Optional[_Iterable[_Union[Notification, _Mapping]]] = ..., error: _Optional[_Union[Error, _Mapping]] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class CapabilityRequest(_message.Message):
    __slots__ = ("extension",)
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class CapabilityResponse(_message.Message):
    __slots__ = ("supported_models", "supported_encodings", "gNMI_version", "extension")
    SUPPORTED_MODELS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_ENCODINGS_FIELD_NUMBER: _ClassVar[int]
    GNMI_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    supported_models: _containers.RepeatedCompositeFieldContainer[ModelData]
    supported_encodings: _containers.RepeatedScalarFieldContainer[Encoding]
    gNMI_version: str
    extension: _containers.RepeatedCompositeFieldContainer[_gnmi_ext_pb2.Extension]
    def __init__(self, supported_models: _Optional[_Iterable[_Union[ModelData, _Mapping]]] = ..., supported_encodings: _Optional[_Iterable[_Union[Encoding, str]]] = ..., gNMI_version: _Optional[str] = ..., extension: _Optional[_Iterable[_Union[_gnmi_ext_pb2.Extension, _Mapping]]] = ...) -> None: ...

class ModelData(_message.Message):
    __slots__ = ("name", "organization", "version")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    organization: str
    version: str
    def __init__(self, name: _Optional[str] = ..., organization: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
