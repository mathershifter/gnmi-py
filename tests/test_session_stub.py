# -*- coding: utf-8 -*-


"""
Offline coverage for Session.* and api.* using the in-process gNMI stub
server (AUDIT.md Testing #1). The existing tests in test_session.py /
test_api.py only run when GNMI_TARGET points at a live device — these run
unconditionally in CI.
"""

from __future__ import annotations

import grpc
import pytest

from gnmi import api
from gnmi.models import Update
from gnmi.proto import gnmi_pb2 as pb
from gnmi.session import Session

from tests.conftest import STUB_GNMI_VERSION, STUB_HOSTNAME


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


@pytest.fixture
def session(stub_target):
    return Session(
        stub_target, insecure=True, metadata={"username": "u", "password": "p"}
    )


def test_session_capabilities(session, stub_server):
    resp = session.capabilities()
    assert resp.gnmi_version == STUB_GNMI_VERSION
    assert len(resp.supported_encodings) == 2
    assert resp.supported_models[0].name == "openconfig-system"
    md = dict(stub_server.servicer.last_metadata)
    assert md.get("username") == "u"


def test_session_get_echoes_paths(session, stub_server):
    resp = session.get(["/system/config/hostname"])
    assert len(resp.notifications) == 1
    notif = resp.notifications[0]
    assert notif.timestamp == 1
    assert len(notif.updates) == 1
    upd = notif.updates[0]
    assert str(upd.path) == "/system/config/hostname"
    assert upd.value.value == STUB_HOSTNAME
    # Round-trip on the wire: server actually received the request.
    assert stub_server.servicer.last_get_request is not None
    assert len(stub_server.servicer.last_get_request.path) == 1


def test_session_get_propagates_rpc_error(session, stub_server):
    def boom(request, context):
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        context.set_details("not allowed")
        return pb.GetResponse()

    stub_server.servicer.get_handler = boom
    with pytest.raises(grpc.RpcError) as ei:
        session.get(["/x"])
    assert ei.value.code() == grpc.StatusCode.PERMISSION_DENIED


def test_session_set_round_trips_all_ops(session, stub_server):
    resp = session.set(
        deletes=["/a/b"],
        replacements=[("/c/d", "v")],
        updates=[("/e/f", "v")],
    )
    ops = [r.op.name for r in resp.responses]
    assert ops == ["DELETE", "REPLACE", "UPDATE"]
    req = stub_server.servicer.last_set_request
    assert len(req.delete) == 1
    assert len(req.replace) == 1
    assert len(req.update) == 1


def test_session_subscribe_streams_then_sync(session):
    paths = ["/system/config/hostname", "/system/state/hostname"]
    seen_paths: list[str] = []
    saw_sync = False

    for resp in session.subscribe(paths, mode="once"):
        if resp.sync_response:
            saw_sync = True
            break
        for upd in resp.update.updates:
            if isinstance(upd, Update):
                seen_paths.append(str(upd.path))

    assert saw_sync
    assert set(seen_paths) == set(paths)


# ---------------------------------------------------------------------------
# High-level api.* wrappers
# ---------------------------------------------------------------------------


def test_api_capabilities(stub_target):
    resp = api.capabilities(stub_target, insecure=True)
    assert resp.gnmi_version == STUB_GNMI_VERSION


def test_api_get(stub_target):
    notifs = list(api.get(stub_target, ["/system/config/hostname"], insecure=True))
    assert len(notifs) == 1
    assert notifs[0].updates[0].value.value == STUB_HOSTNAME


def test_api_subscribe(stub_target):
    notifs = list(
        api.subscribe(
            stub_target, ["/system/config/hostname"], insecure=True, mode="once"
        )
    )
    # api.subscribe yields notifications only (sync responses are dropped).
    assert len(notifs) == 1


def test_api_delete_replace_update(stub_target, stub_server):
    api.delete(stub_target, ["/a"], insecure=True)
    assert stub_server.servicer.last_set_request.delete
    api.replace(stub_target, [("/b", "v")], insecure=True)
    assert stub_server.servicer.last_set_request.replace
    api.update(stub_target, [("/c", "v")], insecure=True)
    assert stub_server.servicer.last_set_request.update


# ---------------------------------------------------------------------------
# TLS branch in Session._new_channel (AUDIT.md Testing #9)
# ---------------------------------------------------------------------------


def test_session_tls_branch_builds_secure_channel():
    """Without `insecure=True` and with a TLSConfig, Session must build a
    secure gRPC channel using the user's CA + client cert/key."""
    from unittest import mock

    from gnmi import session as session_mod
    from gnmi.session import Session, TLSConfig

    tls = TLSConfig(ca_cert=b"ca", client_cert=b"crt", client_key=b"key")

    captured: dict = {}

    def fake_creds(root_certificates, private_key, certificate_chain):
        captured["root"] = root_certificates
        captured["key"] = private_key
        captured["chain"] = certificate_chain
        return mock.sentinel.creds

    def fake_secure_channel(target, creds, options):
        captured["target"] = target
        captured["creds"] = creds
        return mock.MagicMock()

    with (
        mock.patch.object(
            session_mod, "ssl_channel_credentials", side_effect=fake_creds
        ),
        mock.patch.object(
            session_mod, "secure_channel", side_effect=fake_secure_channel
        ),
    ):
        Session("r1.lab:6030", tls=tls)

    assert captured["root"] == b"ca"
    assert captured["chain"] == b"crt"
    assert captured["key"] == b"key"
    assert captured["target"] == "r1.lab:6030"
    assert captured["creds"] is mock.sentinel.creds


def test_session_requires_tls_or_insecure():
    """Neither flag set: must raise rather than silently make an insecure
    channel."""
    from gnmi.session import Session

    with pytest.raises(ValueError):
        Session("r1.lab:6030")


# ---------------------------------------------------------------------------
# Stream-side error: server returns OK chunks then raises (AUDIT.md #6)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# TLS context branches (T9)
# ---------------------------------------------------------------------------


def test_tls_config_context_with_ca_cert():
    import ssl
    from unittest import mock
    from gnmi.tls import TLSConfig

    tls = TLSConfig(ca_cert=b"ca-data", client_cert=None, client_key=None)
    with mock.patch.object(ssl, "create_default_context") as mock_ctx:
        tls.context
    mock_ctx.assert_called_once_with(cadata=b"ca-data")


def test_tls_config_context_no_verify():
    from gnmi.tls import TLSConfig

    tls = TLSConfig(ca_cert=None, client_cert=None, client_key=None, no_verify=True)
    ctx = tls.context
    assert ctx.check_hostname is False


def test_tls_config_context_default():
    import ssl
    from unittest import mock
    from gnmi.tls import TLSConfig

    tls = TLSConfig(ca_cert=None, client_cert=None, client_key=None)
    with mock.patch.object(ssl, "create_default_context") as mock_ctx:
        tls.context
    mock_ctx.assert_called_once_with()


# ---------------------------------------------------------------------------
# Integration gaps (T10)
# ---------------------------------------------------------------------------


def test_set_then_get_round_trip(session, stub_server):
    session.set(updates=[("/x/y", "round-trip-val")])
    resp = session.get(["/x/y"])
    upd = resp.notifications[0].updates[0]
    assert upd.value.value == "round-trip-val"


def test_session_get_multi_path(session):
    resp = session.get(["/a", "/b", "/c"])
    paths = []
    for n in resp.notifications:
        for u in n.updates:
            paths.append(str(u.path))
    assert set(paths) == {"/a", "/b", "/c"}


def test_session_set_with_prefix(session, stub_server):
    session.set(prefix="/system", updates=[("/config/hostname", "new")])
    req = stub_server.servicer.last_set_request
    assert req.prefix.elem[0].name == "system"


def test_session_context_manager_closes_channel(stub_target):
    with Session(stub_target, insecure=True) as sess:
        sess.capabilities()
        channel = sess._channel
    # After exiting the context manager, the channel should be closed.
    # gRPC channels don't expose an is_closed property, but calling
    # an RPC on a closed channel raises.
    with pytest.raises(Exception):
        list(channel.unary_unary("/gnmi.gNMI/Capabilities")(b""))


# ---------------------------------------------------------------------------
# Stream-side error (AUDIT.md #6)
# ---------------------------------------------------------------------------


def test_session_subscribe_propagates_stream_error(session, stub_server):
    """A non-OK status mid-stream must surface as grpc.RpcError on the
    next yield, not silently terminate."""

    def boom(request_iterator, context):
        # Consume the request, then fail with PERMISSION_DENIED.
        for _ in request_iterator:
            break
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        context.set_details("nope")
        return
        yield  # pragma: no cover - keep generator type

    stub_server.servicer.subscribe_handler = boom

    with pytest.raises(grpc.RpcError) as ei:
        list(session.subscribe(["/a"], mode="once"))
    assert ei.value.code() == grpc.StatusCode.PERMISSION_DENIED
