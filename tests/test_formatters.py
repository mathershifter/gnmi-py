# -*- coding: utf-8 -*-

import json

from gnmi.models.notification import Notification
from gnmi.models.update import Update
from gnmi.models.path import Path, PathElem
from gnmi.models.value import ValueType
from gnmi.models.capabilities import CapabilityResponse
from gnmi.models.model_data import ModelData
from gnmi.models.encoding import Encoding

from gnmi.formatters.json import JsonNotification, JsonCapabilities
from gnmi.formatters.pretty import PrettyNotification, PrettyCapabilities
from gnmi.formatters.streams import StreamingNotification, JsonLinesNotification


def _notif(updates=None, deletes=None, prefix=None):
    return Notification(
        timestamp=1_000_000_000,
        prefix=prefix or Path(elem=[]),
        updates=updates or [],
        deletes=deletes or [],
    )


def _cap():
    return CapabilityResponse(
        gnmi_version="0.10.0",
        supported_encodings=[Encoding.JSON, Encoding.PROTO],
        supported_models=[
            ModelData(name="openconfig-system", organization="OC", version="1.0")
        ],
    )


# ---------------------------------------------------------------------------
# JsonNotification
# ---------------------------------------------------------------------------


def test_json_notification_send(capsys):
    n = _notif(
        updates=[Update(path="/a/b", value=("hello", ValueType.STRING_VAL))],
        deletes=[Path.from_str("/x/y")],
    )
    JsonNotification().send(n)
    out = json.loads(capsys.readouterr().out.strip())
    assert out["timestamp"] == 1_000_000_000
    assert out["updates"][0]["path"] == "/a/b"
    assert out["updates"][0]["val"] == "hello"
    assert out["deletes"][0]["path"] == "/x/y"


def test_json_notification_send_empty(capsys):
    n = _notif()
    JsonNotification().send(n)
    out = json.loads(capsys.readouterr().out.strip())
    assert out["updates"] == []
    assert out["deletes"] == []


def test_json_notification_send_with_prefix_target(capsys):
    n = _notif(
        prefix=Path(elem=[PathElem(name="system")], target="r1"),
        updates=[Update(path="/config", value=("v", ValueType.STRING_VAL))],
    )
    JsonNotification().send(n)
    out = json.loads(capsys.readouterr().out.strip())
    assert out["target"] == "r1"


# ---------------------------------------------------------------------------
# JsonCapabilities
# ---------------------------------------------------------------------------


def test_json_capabilities_send(capsys):
    JsonCapabilities().send(_cap())
    out = json.loads(capsys.readouterr().out.strip())
    assert out["gnmi_version"] == "0.10.0"
    assert "JSON" in out["supported_encodings"]
    assert out["supported_models"][0]["name"] == "openconfig-system"


# ---------------------------------------------------------------------------
# PrettyNotification / PrettyCapabilities
# ---------------------------------------------------------------------------


def test_pretty_notification_send(capsys):
    n = _notif(updates=[Update(path="/a", value=("v", ValueType.STRING_VAL))])
    PrettyNotification().send(n)
    assert len(capsys.readouterr().out) > 0


def test_pretty_capabilities_send(capsys):
    PrettyCapabilities().send(_cap())
    out = capsys.readouterr().out
    assert "gNMI Version:" in out
    assert "openconfig-system" in out


# ---------------------------------------------------------------------------
# StreamingNotification / JsonLinesNotification
# ---------------------------------------------------------------------------


def test_streaming_notification_send(capsys):
    n = _notif(
        updates=[Update(path="/a", value=("v", ValueType.STRING_VAL))],
        deletes=[Path.from_str("/b")],
    )
    StreamingNotification().send(n)
    out = capsys.readouterr().out
    assert "UPDATE" in out
    assert "DELETE" in out


def test_json_lines_notification_send(capsys):
    n = _notif(
        updates=[
            Update(path="/a", value=("v1", ValueType.STRING_VAL)),
            Update(path="/b", value=("v2", ValueType.STRING_VAL)),
        ],
    )
    JsonLinesNotification().send(n)
    lines = [
        line for line in capsys.readouterr().out.strip().splitlines() if line.strip()
    ]
    assert len(lines) == 2
    parsed = json.loads(lines[0])
    assert parsed["path"] == "/a"
