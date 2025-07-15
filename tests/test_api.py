# -*- coding: utf-8 -*-
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import pytest

from gnmi import capabilites, get, replace, update, subscribe
from gnmi.models import CapabilityResponse, Update, Path
from tests.conftest import GNMI_AUTH, GNMI_TARGET

pytestmark = pytest.mark.skipif(not GNMI_TARGET, reason="gNMI target not set")


def test_cap(target, is_insecure, tlsconfig):
    response = capabilites(
        target, insecure=is_insecure, tls=tlsconfig, auth=GNMI_AUTH
    )

    assert isinstance(response, CapabilityResponse), "Invalid response"


def test_get(target, is_insecure, tlsconfig):
    resp = get(
        target,
        paths=["/system/config/hostname"],
        insecure=is_insecure,
        tls=tlsconfig,
        auth=GNMI_AUTH,
    )

    for notif in resp:
        for u in notif.updates:
            assert str(u.path) == "/system/config/hostname"
            assert isinstance(u.value.value, str)


def test_subscribe(target, is_insecure, tlsconfig):
    resp = subscribe(
        target,
        paths=["/system/processes/process", "/interfaces/interface"],
        insecure=is_insecure,
        tls=tlsconfig,
        auth=GNMI_AUTH,
        timeout=2
    )

    seen = {}
    for notif in resp:
        for u in notif.updates:
            if isinstance(u, Update):
                path = str(u.path)
                if path.startswith("/system/processes/process"):
                    seen["/system/processes/process"] = True

                if path.startswith("/interfaces/interface"):
                    seen["/interfaces/interface"] = True

            elif isinstance(u, Path): ...
                # print(f"DELETED: {path}")

    assert "/system/processes/process" in seen.keys()
    assert "/interfaces/interface" in seen.keys()


def test_set(target, is_insecure, tlsconfig, request):
    def _get_hostname():
        resp = get(
            target,
            ["/system/config/hostname"],
            insecure=is_insecure,
            tls=tlsconfig,
            auth=GNMI_AUTH,
        )

        for notif in resp:
            for u in notif.updates:
                return u.value

        return None

    hostname = _get_hostname()

    def _rollback():
        hostname_ = _get_hostname()
        if hostname_ != hostname:
            update(
                GNMI_TARGET,
                updates=[("/system/config/hostname", hostname)],
                insecure=is_insecure,
                tls=tlsconfig,
                auth=GNMI_AUTH,
            )

    request.addfinalizer(_rollback)

    updates = [("/system/config/hostname", "minemeow")]
    gen = update(
        target,
        updates=updates,
        insecure=is_insecure,
        tls=tlsconfig,
        auth=GNMI_AUTH,
    )
    for _ in gen.responses:
        pass

    replacements = [("/system/config", {"hostname": hostname})]
    gen = replace(
        target,
        replacements=replacements,
        insecure=is_insecure,
        tls=tlsconfig,
        auth=GNMI_AUTH,
    )

    for _ in gen.responses:
        pass
