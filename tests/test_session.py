import os
import pytest
from tests.conftest import GNMI_PASS, GNMI_TARGET, GNMI_INSECURE, GNMI_USER
from gnmi.session import Session
from gnmi.exceptions import GrpcError, GrpcDeadlineExceeded
from gnmi.models import Update, Path

GNMI_PATHS = os.environ.get("GNMI_PATHS", "/system/config;/system/memory/state")


@pytest.fixture()
def paths():
    return GNMI_PATHS.split(";")

@pytest.fixture()
def session(target, tlsconfig):
    metadata = {"username": GNMI_USER, "password": GNMI_PASS}
    if GNMI_INSECURE:
        insecure = True
    else:
        insecure = False
    return Session(
        target, insecure=insecure, tls=tlsconfig, metadata=metadata
    )

@pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")
def test_cap(session):
    resp = session.capabilities()
    assert len(resp.supported_encodings)

@pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")
def test_get(session, paths):
    resp = session.get(paths)
    for notif in resp.notifications:
        assert notif.timestamp is not None
        for update in notif.updates:
            assert type(update) is Update
            assert type(update.path) is Path
            assert hasattr(update, "value")

@pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")
def test_sub(session, paths):
    with pytest.raises(GrpcDeadlineExceeded):
        for resp in session.subscribe(paths, timeout=2):
            if resp.sync_response:
                continue
            for resp.update in resp.update.updates:
                pass

@pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")
def test_sub_sync_response(session, paths):
    for resp in session.subscribe(paths):
        if resp.sync_response:
            break

@pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")
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

