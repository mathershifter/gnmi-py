# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import json

import pytest

from gnmi import cli
from gnmi.cli import (
    arg_loader,
    format_version,
    load_rc,
    parse_args,
    write_notification,
)
from gnmi.config import Capabilities, Config, Get, Subscription, Subscribe
from gnmi.models.notification import Notification
from gnmi.models.path import Path
from gnmi.models.update import Update
from gnmi.models.value import Value, ValueType

def test_arg_loader():
    tests = [
        (
            [
                "ceos1:6030", "capabilities"
            ],
            Config(
                target="ceos1:6030",
                capabilities=Capabilities()
            )
        ),
        (
            [
                "--prefix", "/interfaces",
                "--get-type", "all",
                "--encoding", "json",
                "ceos1:6030", "get",
                "interface[name=Ethernet3/1/1]/state/counters",
                "interface[name=Ethernet3/2/1.1000]/state/counters",
            ],
            Config(
                target="ceos1:6030",
                get=Get(
                    paths=[
                        "interface[name=Ethernet3/1/1]/state/counters",
                        "interface[name=Ethernet3/2/1.1000]/state/counters"
                    ],
                    prefix="/interfaces",
                    type="all",
                ),
            )
        ),
        (
            [
                "--qos", "0",
                "--mode", "once",
                "--submode", "on-change",
                "--encoding", "json",
                # "--heartbeat", "10s",
                "--prefix", "/interfaces",
                "ceos1:6030", "subscribe",
                "interface/state/counters",
            ],
        
            Config(
                target="ceos1:6030",
                subscribe=Subscribe(
                    
                    subscriptions=[
                        Subscription(
                            path="interface/state/counters",
                            mode="on-change",
                            # heartbeat_interval=10*1_000_000_000
                        ),
                    ],
                    prefix="/interfaces",
                    mode="once"
                )
            )
        )
    ]
    
    for t in tests:
        args, want = t
        cnf = Config(**arg_loader(parse_args(args)))  # type: ignore
        assert cnf == want


# ---------------------------------------------------------------------------
# format_version
# ---------------------------------------------------------------------------

def test_format_version_includes_grpc_and_protobuf():
    s = format_version()
    assert s.startswith("gnmip ")
    assert "protobuf" in s
    assert "grpcio" in s


# ---------------------------------------------------------------------------
# arg_loader — --tls-cert branch (AUDIT bug #2 regression)
# ---------------------------------------------------------------------------

def test_arg_loader_tls_branch_does_not_crash():
    # AUDIT bug #2 was that the TLS argparse name and the attribute lookup
    # disagreed (`tls_get_server_certificates` vs `tls_get_target_certificates`).
    # This call exercises the branch that used to AttributeError.
    args = parse_args([
        "--tls-ca", "ca.pem",
        "--tls-cert", "client.pem",
        "--tls-key", "client.key",
        "--tls-get-server-certificates",
        "r1:6030", "capabilities",
    ])
    loaded = arg_loader(args)
    assert loaded["tls"] == {
        "ca_cert": "ca.pem",
        "cert": "client.pem",
        "key": "client.key",
        "get_server_certificates": True,
    }


def test_arg_loader_no_tls_omits_section():
    args = parse_args(["r1:6030", "capabilities"])
    loaded = arg_loader(args)
    assert "tls" not in loaded


# ---------------------------------------------------------------------------
# write_notification
# ---------------------------------------------------------------------------

def _make_notification() -> Notification:
    n = Notification(timestamp=42, prefix="/system")
    n.updates = [
        Update(path="/config/hostname", value=Value("r1", ValueType.STRING_VAL))
    ]
    n.deletes = [Path.from_str("/state/stale")]
    return n


def test_write_notification_emits_json(capsys):
    write_notification(_make_notification())
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["timestamp"] == 42
    assert payload["prefix"] == "/system"
    assert payload["updates"] == [{"path": "/config/hostname", "value": "r1"}]
    assert payload["deletes"] == [{"path": "/state/stale"}]


def test_write_notification_pretty_indents(capsys):
    write_notification(_make_notification(), pretty=True)
    out = capsys.readouterr().out
    # Pretty mode = indented JSON; presence of a newline + indentation is
    # the easiest behavioral check.
    assert "\n" in out
    assert json.loads(out)["timestamp"] == 42


def test_write_notification_skips_empty_sections(capsys):
    # timestamp=0 and no updates/deletes -> the only key emitted is
    # `prefix`, which write_notification always derives from str(n.prefix)
    # (an empty Path stringifies to "/").
    write_notification(Notification(timestamp=0))
    payload = json.loads(capsys.readouterr().out)
    assert "timestamp" not in payload
    assert "updates" not in payload
    assert "deletes" not in payload


# ---------------------------------------------------------------------------
# load_rc — file resolution via GNMIRC_PATH
# ---------------------------------------------------------------------------

def test_load_rc_returns_empty_config_when_no_rc_file(monkeypatch, tmp_path):
    # Point search dir at an empty directory.
    monkeypatch.setattr(cli, "GNMIRC_PATH", str(tmp_path))
    cnf = load_rc()
    assert isinstance(cnf, Config)
    # Empty-config sentinel: no target, no operation sections.
    assert cnf.target in ("", None) or cnf.target == "localhost:50051"


def test_load_rc_reads_existing_rc_file(monkeypatch, tmp_path):
    # `.gnmirc` is treated as TOML by load_config_file.
    (tmp_path / ".gnmirc").write_text('target = "r1.lab:6030"\ninsecure = true\n')
    monkeypatch.setattr(cli, "GNMIRC_PATH", str(tmp_path))
    cnf = load_rc()
    assert cnf.target == "r1.lab:6030"
    assert cnf.insecure is True


