import os

import pytest

from tests.conftest import (
    GNMI_PASS,
    GNMI_USER,
    requires_live_target,
)

from gnmi.session import Session
from gnmi.exceptions import GrpcError, GrpcDeadlineExceeded
from gnmi.models import Update, Path

GNMI_PATHS = os.environ.get("GNMI_PATHS", "/system/config;/system/memory/state")


@pytest.fixture()
def paths():
    return GNMI_PATHS.split(";")

@pytest.fixture()
def session(target, tlsconfig, is_insecure):
    metadata = {"username": GNMI_USER, "password": GNMI_PASS}
    return Session(
        target, insecure=is_insecure, tls=tlsconfig, metadata=metadata
    )

def test_cap(session):
    resp = session.capabilities()
    assert len(resp.supported_encodings)

def test_get(session, paths):
    resp = session.get(paths)
    for notif in resp.notifications:
        assert notif.timestamp is not None
        for update in notif.updates:
            assert type(update) is Update
            assert type(update.path) is Path
            assert hasattr(update, "value")

@requires_live_target
def test_sub(session, paths):
    with pytest.raises(GrpcDeadlineExceeded):
        for resp in session.subscribe(paths, timeout=2):
            if resp.sync_response:
                continue
            for resp.update in resp.update.updates:
                pass

def test_sub_sync_response(session, paths):
    for resp in session.subscribe(paths, mode="once"):
        if resp.sync_response:
            break

@requires_live_target
def test_set(session):
    path = "/system/config/hostname"

    def _get_hostname():
        return session.get([path]).notifications[0].updates[0].value.value

    hostname_ = _get_hostname()

    invalid = [
        ("/system/config/hostname", 1.1),
    ]

    with pytest.raises(GrpcError):
        rsps = session.set(replacements=invalid)
        assert rsps.responses[0].op.name == "INVALID"

    replacements = [
        ("/system/config/hostname", "minemeow"),
    ]

    rsps = session.set(replacements=replacements)
    assert rsps.responses[0].op.name == "REPLACE"

    _ = session.get(["/system/config/hostname"])

    assert _get_hostname() == "minemeow"

    updates = [("/system/config", {"hostname": hostname_})]

    rsps = session.set(updates=updates)
    assert rsps.responses[0].op.name == "UPDATE"
    assert _get_hostname() == hostname_

