# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Coverage for gnmi.tls.get_server_certificate (AUDIT.md Testing #3)."""

from __future__ import annotations

import socket
import ssl
from unittest import mock

import pytest

from gnmi import tls as tls_mod
from gnmi.models.target import Target


def test_get_server_certificate_uses_provided_context_and_returns_der():
    fake_der = b"\x30\x82DERBYTES"

    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = fake_der

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn) as cc:
        got = tls_mod.get_server_certificate(
            Target(address="r1.lab:6030"), context=ctx
        )

    assert got == fake_der
    cc.assert_called_once_with(("r1.lab", 6030))
    ctx.wrap_socket.assert_called_once_with(conn, server_hostname="r1.lab")
    # Default form is DER (binary_form=True).
    sconn.getpeercert.assert_called_once_with(binary_form=True)


def test_get_server_certificate_pem_form():
    fake_der = b"\x30\x82DERBYTES"

    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = fake_der

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn), \
         mock.patch.object(ssl, "DER_cert_to_PEM_cert",
                           return_value="-----BEGIN CERT-----...\n") as conv:
        got = tls_mod.get_server_certificate(
            Target(address="r1.lab:6030"), context=ctx, pem=True
        )

    conv.assert_called_once_with(fake_der)
    assert got == b"-----BEGIN CERT-----...\n"


def test_get_server_certificate_returns_none_when_no_cert():
    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = None

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn):
        got = tls_mod.get_server_certificate(
            Target(address="r1.lab:6030"), context=ctx
        )
    assert got is None


def test_get_server_certificate_propagates_handshake_failure():
    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.side_effect = ssl.SSLCertVerificationError("bad chain")

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(socket, "create_connection", return_value=conn):
        with pytest.raises(ssl.SSLCertVerificationError):
            tls_mod.get_server_certificate(
                Target(address="r1.lab:6030"), context=ctx
            )


def test_get_server_certificate_default_context_when_none_provided():
    sconn = mock.MagicMock()
    sconn.__enter__.return_value = sconn
    sconn.getpeercert.return_value = b""

    ctx = mock.MagicMock(spec=ssl.SSLContext)
    ctx.wrap_socket.return_value = sconn

    conn = mock.MagicMock()
    conn.__enter__.return_value = conn

    with mock.patch.object(ssl, "create_default_context", return_value=ctx) as cdc, \
         mock.patch.object(socket, "create_connection", return_value=conn):
        tls_mod.get_server_certificate(Target(address="r1.lab:6030"))

    cdc.assert_called_once()
