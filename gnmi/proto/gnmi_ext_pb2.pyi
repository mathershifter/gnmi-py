from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtensionID(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EID_UNSET: _ClassVar[ExtensionID]
    EID_EXPERIMENTAL: _ClassVar[ExtensionID]
EID_UNSET: ExtensionID
EID_EXPERIMENTAL: ExtensionID

class Extension(_message.Message):
    __slots__ = ("registered_ext", "master_arbitration", "history", "commit", "depth", "config_subscription")
    REGISTERED_EXT_FIELD_NUMBER: _ClassVar[int]
    MASTER_ARBITRATION_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    CONFIG_SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    registered_ext: RegisteredExtension
    master_arbitration: MasterArbitration
    history: History
    commit: Commit
    depth: Depth
    config_subscription: ConfigSubscription
    def __init__(self, registered_ext: _Optional[_Union[RegisteredExtension, _Mapping]] = ..., master_arbitration: _Optional[_Union[MasterArbitration, _Mapping]] = ..., history: _Optional[_Union[History, _Mapping]] = ..., commit: _Optional[_Union[Commit, _Mapping]] = ..., depth: _Optional[_Union[Depth, _Mapping]] = ..., config_subscription: _Optional[_Union[ConfigSubscription, _Mapping]] = ...) -> None: ...

class RegisteredExtension(_message.Message):
    __slots__ = ("id", "msg")
    ID_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    id: ExtensionID
    msg: bytes
    def __init__(self, id: _Optional[_Union[ExtensionID, str]] = ..., msg: _Optional[bytes] = ...) -> None: ...

class MasterArbitration(_message.Message):
    __slots__ = ("role", "election_id")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    ELECTION_ID_FIELD_NUMBER: _ClassVar[int]
    role: Role
    election_id: Uint128
    def __init__(self, role: _Optional[_Union[Role, _Mapping]] = ..., election_id: _Optional[_Union[Uint128, _Mapping]] = ...) -> None: ...

class Uint128(_message.Message):
    __slots__ = ("high", "low")
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    high: int
    low: int
    def __init__(self, high: _Optional[int] = ..., low: _Optional[int] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class History(_message.Message):
    __slots__ = ("snapshot_time", "range")
    SNAPSHOT_TIME_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    snapshot_time: int
    range: TimeRange
    def __init__(self, snapshot_time: _Optional[int] = ..., range: _Optional[_Union[TimeRange, _Mapping]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("start", "end")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: int
    end: int
    def __init__(self, start: _Optional[int] = ..., end: _Optional[int] = ...) -> None: ...

class Commit(_message.Message):
    __slots__ = ("id", "commit", "confirm", "cancel", "set_rollback_duration")
    ID_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    CONFIRM_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    SET_ROLLBACK_DURATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    commit: CommitRequest
    confirm: CommitConfirm
    cancel: CommitCancel
    set_rollback_duration: CommitSetRollbackDuration
    def __init__(self, id: _Optional[str] = ..., commit: _Optional[_Union[CommitRequest, _Mapping]] = ..., confirm: _Optional[_Union[CommitConfirm, _Mapping]] = ..., cancel: _Optional[_Union[CommitCancel, _Mapping]] = ..., set_rollback_duration: _Optional[_Union[CommitSetRollbackDuration, _Mapping]] = ...) -> None: ...

class CommitRequest(_message.Message):
    __slots__ = ("rollback_duration",)
    ROLLBACK_DURATION_FIELD_NUMBER: _ClassVar[int]
    rollback_duration: _duration_pb2.Duration
    def __init__(self, rollback_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class CommitConfirm(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CommitCancel(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CommitSetRollbackDuration(_message.Message):
    __slots__ = ("rollback_duration",)
    ROLLBACK_DURATION_FIELD_NUMBER: _ClassVar[int]
    rollback_duration: _duration_pb2.Duration
    def __init__(self, rollback_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class Depth(_message.Message):
    __slots__ = ("level",)
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    level: int
    def __init__(self, level: _Optional[int] = ...) -> None: ...

class ConfigSubscription(_message.Message):
    __slots__ = ("start", "sync_done")
    START_FIELD_NUMBER: _ClassVar[int]
    SYNC_DONE_FIELD_NUMBER: _ClassVar[int]
    start: ConfigSubscriptionStart
    sync_done: ConfigSubscriptionSyncDone
    def __init__(self, start: _Optional[_Union[ConfigSubscriptionStart, _Mapping]] = ..., sync_done: _Optional[_Union[ConfigSubscriptionSyncDone, _Mapping]] = ...) -> None: ...

class ConfigSubscriptionStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigSubscriptionSyncDone(_message.Message):
    __slots__ = ("commit_confirm_id", "server_commit_id", "done")
    COMMIT_CONFIRM_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_COMMIT_ID_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    commit_confirm_id: str
    server_commit_id: str
    done: bool
    def __init__(self, commit_confirm_id: _Optional[str] = ..., server_commit_id: _Optional[str] = ..., done: bool = ...) -> None: ...
