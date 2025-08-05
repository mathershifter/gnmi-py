import gnmi_pb2 as _gnmi_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Configuration(_message.Message):
    __slots__ = ("request", "target", "instance_id", "meta", "revision")
    class RequestEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _gnmi_pb2.SubscribeRequest
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_gnmi_pb2.SubscribeRequest, _Mapping]] = ...) -> None: ...
    class TargetEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Target
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Target, _Mapping]] = ...) -> None: ...
    class MetaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    request: _containers.MessageMap[str, _gnmi_pb2.SubscribeRequest]
    target: _containers.MessageMap[str, Target]
    instance_id: str
    meta: _containers.ScalarMap[str, str]
    revision: int
    def __init__(self, request: _Optional[_Mapping[str, _gnmi_pb2.SubscribeRequest]] = ..., target: _Optional[_Mapping[str, Target]] = ..., instance_id: _Optional[str] = ..., meta: _Optional[_Mapping[str, str]] = ..., revision: _Optional[int] = ...) -> None: ...

class Target(_message.Message):
    __slots__ = ("addresses", "credentials", "request", "meta", "dialer")
    class MetaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    DIALER_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedScalarFieldContainer[str]
    credentials: Credentials
    request: str
    meta: _containers.ScalarMap[str, str]
    dialer: str
    def __init__(self, addresses: _Optional[_Iterable[str]] = ..., credentials: _Optional[_Union[Credentials, _Mapping]] = ..., request: _Optional[str] = ..., meta: _Optional[_Mapping[str, str]] = ..., dialer: _Optional[str] = ...) -> None: ...

class Credentials(_message.Message):
    __slots__ = ("username", "password", "password_id")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_ID_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    password_id: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ..., password_id: _Optional[str] = ...) -> None: ...
