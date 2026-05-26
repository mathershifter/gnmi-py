# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Coverage for gnmi.certs.get_server_certificate (AUDIT.md Testing #3)."""

from __future__ import annotations

import socket
import ssl
from unittest import mock

import pytest

from gnmi import certs
from gnmi.models.target import Target


def test_get_server_certificate_uses_provided_context_and_returns_peer_cert():
    fake_peer = {"subject": ((("commonName", "r1.lab"),),)}

    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = fake_peer

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn) as cc:
        got = certs.get_server_certificate(Target(address="r1.lab:6030"), context=ctx)

    assert got == fake_peer
    cc.assert_called_once_with(("r1.lab", 6030))
    ctx.wrap_socket.assert_called_once_with(conn, server_hostname="r1.lab")


def test_get_server_certificate_propagates_handshake_failure():
    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.side_effect = ssl.SSLCertVerificationError("bad chain")

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn):
        with pytest.raises(ssl.SSLCertVerificationError):
            certs.get_server_certificate(
                Target(address="r1.lab:6030"), context=ctx
            )


def test_get_server_certificate_default_context_when_none_provided():
    # When context is None, the function must build a default one.
    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = {}

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(ssl, "create_default_context", return_value=ctx) as cdc, \
         mock.patch.object(socket, "create_connection", return_value=conn):
        certs.get_server_certificate(Target(address="r1.lab:6030"))

    cdc.assert_called_once()
