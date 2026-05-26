# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Coverage for gnmi.async_session.AsyncSession.

The grpc.aio client can talk to the same sync stub server used by
test_session_stub.py, so these tests reuse the `stub_server` fixture and
drive AsyncSession via `asyncio.run` — no pytest-asyncio dep needed.

Each xfail test names the AsyncSession bug it covers in its reason
string so the test surface doubles as a defect catalog.
"""
from __future__ import annotations

import asyncio
from unittest import mock

import grpc
import pytest

from gnmi import async_session as async_mod
from gnmi.async_session import AsyncSession, TLSConfig as AsyncTLSConfig

from tests.conftest import STUB_GNMI_VERSION, STUB_HOSTNAME


def _run(coro):
    """Drive an async test function from a sync test."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

def test_async_capabilities(stub_server):
    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            return await sess.capabilities()
        finally:
            await sess._channel.close(None)

    resp = _run(go())
    assert resp.gnmi_version == STUB_GNMI_VERSION


def test_async_get_echoes_paths(stub_server):
    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            return await sess.get(["/system/config/hostname"])
        finally:
            await sess._channel.close(None)

    resp = _run(go())
    assert len(resp.notifications) == 1
    upd = resp.notifications[0].updates[0]
    assert str(upd.path) == "/system/config/hostname"
    assert upd.value.value == STUB_HOSTNAME


def test_async_set_round_trips_all_ops(stub_server):
    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            return await sess.set(
                deletes=["/a/b"],
                replacements=[("/c/d", "v")],
                updates=[("/e/f", "v")],
            )
        finally:
            await sess._channel.close(None)

    resp = _run(go())
    assert [r.op.name for r in resp.responses] == ["DELETE", "REPLACE", "UPDATE"]


def test_async_subscribe_streams_then_sync(stub_server):
    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            seen = []
            saw_sync = False
            async for resp in sess.subscribe(["/a", "/b"], mode="once"):
                if resp.sync_response:
                    saw_sync = True
                    break
                for upd in resp.update.updates:
                    seen.append(str(upd.path))
            return seen, saw_sync
        finally:
            await sess._channel.close(None)

    seen, saw_sync = _run(go())
    assert saw_sync
    assert set(seen) == {"/a", "/b"}


def test_async_session_string_target_now_accepted(stub_server):
    """Regression for the prior API mismatch — AsyncSession now wraps a
    string target the way sync Session does."""

    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            return await sess.capabilities()
        finally:
            await sess._channel.close(None)

    assert _run(go()).gnmi_version == STUB_GNMI_VERSION


def test_async_session_requires_tls_or_insecure():
    """Neither flag set must raise (mirror sync Session)."""
    sess = AsyncSession.__new__(AsyncSession)
    sess._target = mock.MagicMock(address="r1.lab:6030")
    sess._tls = None
    sess._insecure = False
    sess._grpc_options = {}.items()
    with pytest.raises(ValueError):
        sess._new_channel()


def test_async_session_dict_metadata_is_iterable_of_pairs(stub_server):
    """String-valued dict metadata must flow through to the server as
    (key, value) pairs."""

    async def go():
        sess = AsyncSession(
            stub_server.target,
            insecure=True,
            metadata={"username": "u", "password": "p"},
        )
        try:
            await sess.capabilities()
        finally:
            await sess._channel.close(None)

    _run(go())
    md = dict(stub_server.servicer.last_metadata)
    assert md.get("username") == "u"
    assert md.get("password") == "p"


def test_async_session_get_server_cert_fetches_pem(stub_server):
    """When get_server_cert=True, AsyncSession must fetch the PEM-encoded
    cert (not the parsed-dict ssl.getpeercert() output) and forward it as
    `root_certificates`."""
    fetched_pem = b"-----BEGIN CERTIFICATE-----FETCHED-----END CERTIFICATE-----"
    tls = AsyncTLSConfig(
        ca_cert=b"user-ca",
        client_cert=None,
        client_key=None,
        get_server_cert=True,
    )

    captured: dict = {}

    def fake_creds(root_certificates, private_key, certificate_chain):
        captured["root"] = root_certificates
        return mock.sentinel.creds

    with mock.patch.object(
        AsyncTLSConfig, "context", new_callable=mock.PropertyMock,
        return_value=mock.sentinel.ctx,
    ), mock.patch.object(
        async_mod, "get_server_certificate", return_value=fetched_pem
    ) as fake_fetch, mock.patch.object(
        async_mod, "ssl_channel_credentials", side_effect=fake_creds
    ), mock.patch.object(
        async_mod, "secure_channel", return_value=mock.MagicMock()
    ):
        AsyncSession("r1.lab:6030", tls=tls)

    # Must request the PEM form so the bytes are usable as root_certificates.
    assert fake_fetch.call_args.kwargs.get("pem") is True
    assert captured["root"] == fetched_pem


def test_async_session_tls_branch_builds_secure_channel():
    tls = AsyncTLSConfig(ca_cert=b"ca", client_cert=b"crt", client_key=b"key")

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

    with mock.patch.object(
        async_mod, "ssl_channel_credentials", side_effect=fake_creds
    ), mock.patch.object(
        async_mod, "secure_channel", side_effect=fake_secure_channel
    ):
        AsyncSession("r1.lab:6030", tls=tls)

    assert captured["root"] == b"ca"
    assert captured["chain"] == b"crt"
    assert captured["key"] == b"key"
    assert captured["target"] == "r1.lab:6030"
    assert captured["creds"] is mock.sentinel.creds


def test_async_session_in_package_dunder_all():
    import gnmi

    assert "AsyncSession" in gnmi.__all__


# ---------------------------------------------------------------------------
# Open bugs
# ---------------------------------------------------------------------------

def test_async_session_supports_async_context_manager(stub_server):
    async def go():
        async with AsyncSession(stub_server.target, insecure=True) as sess:
            return await sess.capabilities()

    assert _run(go()).gnmi_version == STUB_GNMI_VERSION


def test_async_session_propagates_rpc_error(stub_server):
    """Native error propagation: AsyncSession surfaces grpc.aio.AioRpcError
    (a subclass of grpc.RpcError) so callers see the gRPC contract
    directly. Matches sync Session, which also propagates grpc.RpcError."""
    from gnmi.proto import gnmi_pb2 as pb

    def boom(request, context):
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        context.set_details("nope")
        return pb.GetResponse()

    stub_server.servicer.get_handler = boom

    async def go():
        sess = AsyncSession(stub_server.target, insecure=True)
        try:
            await sess.get(["/x"])
        finally:
            await sess._channel.close(None)

    with pytest.raises(grpc.RpcError) as ei:
        _run(go())
    assert ei.value.code() == grpc.StatusCode.PERMISSION_DENIED


def test_async_session_normalizes_non_string_metadata_values(stub_server):
    async def go():
        sess = AsyncSession(
            stub_server.target,
            insecure=True,
            metadata={"trace_id": 42},
        )
        try:
            await sess.capabilities()
        finally:
            await sess._channel.close(None)

    _run(go())
    md = dict(stub_server.servicer.last_metadata)
    assert md.get("trace_id") == "42"
