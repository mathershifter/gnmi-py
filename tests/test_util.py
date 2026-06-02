# -*- coding: utf-8 -*-


import pytest

from gnmi.util import escape_string, oneof, parse_duration


def test_parse_duration():
    tests = {
        "1ns": 1,
        "1us": 1000,
        "1ms": 1_000_000,
        "1s": 1_000_000_000,
        "1m": 60_000_000_000,
        "1586ms": 1_586_000_000,
    }
    for s, want in tests.items():
        assert parse_duration(s) == want


# ---------------------------------------------------------------------------
# escape_string (AUDIT.md Testing Nit)
# ---------------------------------------------------------------------------


def test_escape_string_passthrough_when_no_metachars():
    assert escape_string("plain", "/") == "plain"


def test_escape_string_escapes_each_target_char():
    assert escape_string("a/b/c", "/") == "a\\/b\\/c"


def test_escape_string_escapes_backslash_in_addition_to_targets():
    # Backslash is always escaped — needed so the consumer can unambiguously
    # tell a literal backslash from an escape lead.
    assert escape_string("a\\b", "/") == "a\\\\b"


def test_escape_string_supports_multi_char_escape_set():
    # The `escape` arg is treated as a set of characters (every char in
    # the string is added to the metachar list).
    assert escape_string("a]b/c", "]/") == "a\\]b\\/c"


# ---------------------------------------------------------------------------
# oneof error paths (AUDIT.md Testing #6)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# datetime_from_int64, get_datatype, enable_grpc_debuging, prepare_metadata
# ---------------------------------------------------------------------------


def test_datetime_from_int64():
    import datetime
    from gnmi.util import datetime_from_int64

    result = datetime_from_int64(1_000_000_000)
    assert result == datetime.datetime.fromtimestamp(1)


def test_datetime_from_int64_zero():
    import datetime
    from gnmi.util import datetime_from_int64

    result = datetime_from_int64(0)
    assert result == datetime.datetime.fromtimestamp(0)


def test_get_datatype():
    from gnmi.util import get_datatype
    import gnmi.proto.gnmi_pb2 as pb

    assert get_datatype("all") == pb.GetRequest.ALL
    assert get_datatype("config") == pb.GetRequest.CONFIG


def test_enable_grpc_debugging(monkeypatch):
    import os
    from gnmi.util import enable_grpc_debuging

    monkeypatch.delenv("GRPC_TRACE", raising=False)
    monkeypatch.delenv("GRPC_VERBOSITY", raising=False)
    enable_grpc_debuging()
    assert os.environ["GRPC_TRACE"] == "all"
    assert os.environ["GRPC_VERBOSITY"] == "DEBUG"


def test_prepare_metadata_none():
    from gnmi.util import prepare_metadata

    assert prepare_metadata(None) == []


def test_prepare_metadata_dict():
    from gnmi.util import prepare_metadata

    assert prepare_metadata({"a": 1, "b": "x"}) == [("a", "1"), ("b", "x")]


# ---------------------------------------------------------------------------
# Encoding.from_str, SubscriptionMode.from_str, SubscriptionListMode.from_str
# ---------------------------------------------------------------------------


def test_encoding_from_str():
    from gnmi.models.encoding import Encoding

    assert Encoding.from_str("json") == Encoding.JSON
    assert Encoding.from_str("json-ietf") == Encoding.JSON_IETF
    assert Encoding.from_str("proto") == Encoding.PROTO


def test_subscription_mode_from_str():
    from gnmi.models.subscription import SubscriptionMode

    assert (
        SubscriptionMode.from_str("target-defined") == SubscriptionMode.TARGET_DEFINED
    )
    assert SubscriptionMode.from_str("on-change") == SubscriptionMode.ON_CHANGE
    assert SubscriptionMode.from_str("sample") == SubscriptionMode.SAMPLE


def test_subscription_mode_from_str_invalid_raises():
    from gnmi.models.subscription import SubscriptionMode

    with pytest.raises(ValueError):
        SubscriptionMode.from_str("bogus")


def test_subscription_list_mode_from_str():
    from gnmi.models.subscription_list import SubscriptionListMode

    assert SubscriptionListMode.from_str("stream") == SubscriptionListMode.STREAM
    assert SubscriptionListMode.from_str("once") == SubscriptionListMode.ONCE
    assert SubscriptionListMode.from_str("poll") == SubscriptionListMode.POLL


def test_subscription_list_mode_from_str_invalid_raises():
    from gnmi.models.subscription_list import SubscriptionListMode

    with pytest.raises(ValueError):
        SubscriptionListMode.from_str("bogus")


# ---------------------------------------------------------------------------
# oneof error paths (AUDIT.md Testing #6)
# ---------------------------------------------------------------------------


def test_oneof_zero_set_raises():
    with pytest.raises(ValueError):
        oneof(None, None)


def test_oneof_multiple_set_raises():
    with pytest.raises(ValueError):
        oneof("a", "b")


def test_oneof_single_set_returns_index():
    assert oneof("only", None, None) == 0
    assert oneof(None, "only", None) == 1
    assert oneof(None, None, "only") == 2
