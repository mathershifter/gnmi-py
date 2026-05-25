# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Tests covering bugs catalogued in AUDIT.md (critical #3,#6,#7,#8 and
important #9,#10,#11,#12,#13,#14,#15,#16).

Each bug-demonstration test is marked xfail(strict=True) so it records the
defect today and will auto-flip to FAIL once the bug is fixed — that turn
to PASS is the signal to remove the marker.

Bugs #4 and #5 from AUDIT.md were re-verified and dropped: protobuf accepts
enum-name strings (so GetRequest/UpdateResult encode round-trips), and the
DataType factory referenced in #5 no longer exists in the current
descriptor implementation.
"""
from __future__ import annotations

from re import S
import signal
import sys
from unittest import mock

import pytest

from gnmi.models.path import Path
from gnmi.models.subscribe import SubscribeRequest
from gnmi.models.subscription import Subscription
from gnmi.models.subscription_list import SubscriptionList
from gnmi.models.update import update_list_factory
from gnmi.models.value import Value, ValueType
from gnmi.util import escape_string, oneof, parse_duration


# ---------------------------------------------------------------------------
# get_server_cert=True contract — early TLS-validation handshake
# ---------------------------------------------------------------------------
#
# (AUDIT.md bug #3 rescinded after re-read: get_server_certificate performs
# an SSL handshake against the user-provided CA and returns the parsed peer
# cert via ssl.getpeercert() — it's a validation step, not a retrieval, and
# the dict isn't a drop-in root_cert.)
#
# The remaining contract is "validation must actually happen and a failure
# must surface." These two tests lock that in.

def test_session_get_server_cert_invokes_handshake():
    from gnmi import session as session_mod
    from gnmi.session import Session, TLSConfig

    tls = TLSConfig(
        ca_cert=b"ca",
        client_cert=b"cert",
        client_key=b"key",
        get_server_cert=True,
    )

    with mock.patch.object(
        TLSConfig, "context", new_callable=mock.PropertyMock,
        return_value=mock.sentinel.ctx,
    ), mock.patch.object(
        session_mod, "get_server_certificate", return_value={"subject": ()}
    ) as fake_fetch, mock.patch.object(
        session_mod.grpc, "ssl_channel_credentials", return_value=mock.sentinel.creds
    ), mock.patch.object(
        session_mod.grpc, "secure_channel", return_value=mock.MagicMock()
    ):
        Session("localhost:6030", tls=tls)

    assert fake_fetch.called, (
        "get_server_cert=True must trigger the validation handshake."
    )
    # And it must be invoked with the context built from the user's CA,
    # otherwise validation is meaningless.
    _, kwargs = fake_fetch.call_args
    args = fake_fetch.call_args.args
    assert mock.sentinel.ctx in args or kwargs.get("context") is mock.sentinel.ctx


def test_session_get_server_cert_propagates_validation_failure():
    """A handshake failure during the validation step must surface — it
    must not be swallowed by `_ = get_server_certificate(...)`."""
    import ssl

    from gnmi import session as session_mod
    from gnmi.session import Session, TLSConfig

    tls = TLSConfig(
        ca_cert=b"ca",
        client_cert=b"cert",
        client_key=b"key",
        get_server_cert=True,
    )

    with mock.patch.object(
        TLSConfig, "context", new_callable=mock.PropertyMock,
        return_value=mock.sentinel.ctx,
    ), mock.patch.object(
        session_mod,
        "get_server_certificate",
        side_effect=ssl.SSLCertVerificationError("validation failed"),
    ), mock.patch.object(
        session_mod.grpc, "secure_channel", return_value=mock.MagicMock()
    ):
        with pytest.raises(ssl.SSLCertVerificationError):
            Session("localhost:6030", tls=tls)


# ---------------------------------------------------------------------------
# Critical bug #6 — SubscribeRequest.decode is a no-op
# ---------------------------------------------------------------------------

# Bug #6 fixed: SubscribeRequest.decode now honours v.subscribe and v.poll.
# The two round-trip tests below act as regression guards.

def test_subscribe_request_round_trip_preserves_subscribe():
    orig = SubscribeRequest(
        subscribe=SubscriptionList(subscriptions=[Subscription(path="/a/b")])
    )
    decoded = SubscribeRequest.decode(orig.encode())
    assert decoded.subscribe is not None


def test_subscribe_request_round_trip_preserves_poll():
    from gnmi.models.subscribe import Poll

    orig = SubscribeRequest(poll=Poll())
    decoded = SubscribeRequest.decode(orig.encode())
    assert decoded.poll is not None


# ---------------------------------------------------------------------------
# Critical bug #7 — api.subscribe() silently swallows GrpcDeadlineExceeded
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="api.py:220-221 catches GrpcDeadlineExceeded with `pass`; the "
#     "generator terminates silently and callers cannot distinguish a clean "
#     "stream end from a timeout.",
# )
def test_subscribe_propagates_deadline_exceeded():
    from gnmi import api
    from gnmi.exceptions import GrpcDeadlineExceeded

    def _subscribe(*_a, **_kw):
        raise GrpcDeadlineExceeded(mock.MagicMock(code=mock.MagicMock(name="DEADLINE_EXCEEDED")))
        yield  # pragma: no cover - keeps it a generator

    sess = mock.MagicMock()
    sess.subscribe.side_effect = _subscribe
    sess.subscribe.side_effect = _subscribe
    
    cm = mock.MagicMock()
    cm.__enter__.return_value = sess
    cm.__exit__.return_value = False
    with mock.patch.object(api, "Session", return_value=cm):
        gen = api.subscribe("localhost:6030", ["/a"])
        with pytest.raises(GrpcDeadlineExceeded):
            list(gen)


# ---------------------------------------------------------------------------
# Critical bug #8 — oneof() rejects legitimate `False`
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="oneof() (util.py:86) uses `is not None`, so `False` is counted "
#     "as set. A SubscribeResponse with update + default sync_response=False "
#     "fails to encode.",
# )
def test_oneof_treats_false_as_unset():
    # We expect oneof to either skip False (treating it like "not set" for
    # proto-bool fields) or to have an explicit bool-aware contract. Today
    # it counts False as set, breaking SubscribeResponse.encode when both
    # `update` and the default `sync_response=False` are present.
    from gnmi.models.notification import Notification
    from gnmi.models.subscribe import SubscribeResponse

    resp = SubscribeResponse(
        update=Notification(timestamp=0, updates=[], deletes=[]),
        sync_response=False,
    )
    # Should not raise.
    resp.encode()


# ---------------------------------------------------------------------------
# Important bug #9 — Value.encode mis-handles LEAFLIST_VAL of primitives
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="value.py:155-159 calls .encode() on raw list elements; ints/strs "
#     "have no .encode(), so primitive leaflists always crash.",
# )
def test_value_leaflist_of_ints_encodes():
    out = Value([1, 2, 3], ValueType.LEAFLIST_VAL).encode()
    elements = list(out.leaflist_val.element)
    assert [e.int_val for e in elements] == [1, 2, 3]


# ---------------------------------------------------------------------------
# Important bug #10 — Value.encode double-encodes bytes for ANY_VAL
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="value.py:151 wraps bytes with `str(self.val).encode()` -> b\"b'x'\". "
#     "Already-bytes input must be passed through unchanged.",
# )
def test_value_any_val_preserves_bytes():
    raw = b"raw-bytes-payload"
    encoded = Value(raw, ValueType.ANY_VAL).encode()
    assert encoded.any_val.value == raw


# ---------------------------------------------------------------------------
# Important bug #11 — Session leaks gRPC channel (no close / context-manager)
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="Session opens a grpc.Channel in __init__ but exposes no close() "
#     "or context-manager. Every helper in api.py spins up a Session and "
#     "leaks its channel.",
# )
def test_session_supports_close_or_context_manager():
    from gnmi.session import Session

    assert hasattr(Session, "close") or (
        hasattr(Session, "__enter__") and hasattr(Session, "__exit__")
    )


# ---------------------------------------------------------------------------
# Important bug #12 — parse_duration mishandles zero and compound durations
# ---------------------------------------------------------------------------

def test_parse_duration_zero_seconds():
    # "0s" should round-trip cleanly to 0 ns. The current implementation
    # happens to return 0 (because the val>0 guard short-circuits the unit
    # lookup), but only by accident — bare "0" should also work, and today
    # any zero-valued input ignores the unit entirely.
    assert parse_duration("0s") == 0


def test_parse_duration_compound():
    # 1 minute + 30 seconds = 90s in nanoseconds
    assert parse_duration("1m30s") == 90 * 1_000_000_000


def test_parse_duration_rejects_garbage():
    # Regression: the old scanner silently returned 0 for unknown trailing
    # input; the new one must raise.
    with pytest.raises(ValueError):
        parse_duration("1x")
    with pytest.raises(ValueError):
        parse_duration("abc")
    with pytest.raises(ValueError):
        parse_duration("")


# @pytest.mark.xfail(
#     strict=True,
#     reason="The `val > 0` guard at util.py:58 silently drops bare numerics; "
#     "parse_duration('500') returns 0 instead of 500ms (the documented "
#     "default unit).",
# )
def test_parse_duration_bare_number_uses_default_unit():
    assert parse_duration("500") == 500 * 1_000_000


# ---------------------------------------------------------------------------
# Important bug #13 — update_list_factory silently drops non-list sequences
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="update_list_factory's signature is Sequence[UpdateItem_] but the "
#     "isinstance(ul, list) guard silently returns [] for any tuple or other "
#     "Sequence.",
# )
def test_update_list_factory_accepts_tuple_sequence():
    out = update_list_factory((("/a", "v1"), ("/b", "v2")))
    assert len(out) == 2


# ---------------------------------------------------------------------------
# Important bug #14 — Subscriptions descriptor silently drops Path inputs
# ---------------------------------------------------------------------------

# @pytest.mark.xfail(
#     strict=True,
#     reason="Session.subscribe advertises list[str|Path|Subscription], but "
#     "Subscriptions.__set__ filters Path objects out without raising.",
# )
def test_subscriptions_descriptor_accepts_path():
    sl = SubscriptionList(subscriptions=[Path.from_str("/a/b")])
    assert len(list(sl.subscriptions)) == 1


def test_subscription_list_constructs_with_no_args():
    sl = SubscriptionList()
    assert list(sl.subscriptions) == []


def test_get_request_constructs_with_no_args():
    # Same descriptor pattern affects Paths in GetRequest.
    from gnmi.models.get import GetRequest

    req = GetRequest()
    assert list(req.paths) == []


def test_set_request_constructs_with_no_args():
    # Same descriptor pattern affects Paths and Updates in SetRequest.
    from gnmi.models.set import SetRequest

    req = SetRequest()
    assert list(req.deletes) == []
    assert list(req.replacements) == []
    assert list(req.updates) == []
    assert list(req.union_replacements) == []


def test_notification_constructs_with_no_args():
    from gnmi.models.notification import Notification

    n = Notification(timestamp=0)
    assert list(n.deletes) == []
    assert list(n.updates) == []


# ---------------------------------------------------------------------------
# Important bug #15 — gnmi.entry installs SIGINT handler at import time
# ---------------------------------------------------------------------------

def test_importing_entry_does_not_change_sigint_handler():
    # Force a clean re-import so we can compare before/after.
    sys.modules.pop("gnmi.entry", None)
    before = signal.getsignal(signal.SIGINT)
    try:
        import gnmi.entry  # noqa: F401
        after = signal.getsignal(signal.SIGINT)
        assert after is before
    finally:
        # Best-effort restore so we don't leak state into other tests.
        signal.signal(signal.SIGINT, before)


# ---------------------------------------------------------------------------
# escape_string + path parser round-trip
# ---------------------------------------------------------------------------
#
# (AUDIT.md bug #16 rescinded: escape_string is a one-way escape over the
# raw field, not an idempotent transform. The real contract is "Path
# stringify-then-parse round-trips losslessly even when names contain
# escape-significant characters." This guards that.)

def test_path_string_round_trip_preserves_backslash_in_name():
    from gnmi.models.path import Path, PathElem

    original = Path(elem=[PathElem(name="a\\b")])
    parsed = Path.from_str(str(original))
    assert [e.name for e in parsed.elem] == ["a\\b"]


def test_escape_string_escapes_target_and_backslash():
    # Documented contract: every char in `escape` plus '\\' is prefixed
    # with a backslash; other chars pass through.
    assert escape_string("plain", "/") == "plain"
    assert escape_string("a/b", "/") == "a\\/b"
    assert escape_string("a\\b", "/") == "a\\\\b"


def test_oneof_baseline_still_works():
    # Sanity guard so we notice if the oneof contract changes more broadly.
    assert oneof("only", None, None) == 0
    assert oneof(None, "only", None) == 1
