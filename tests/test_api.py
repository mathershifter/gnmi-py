# -*- coding: utf-8 -*-
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from typing import Any

from gnmi import capabilities, get, replace, update, subscribe
from gnmi.models import CapabilityResponse, Update, Path
from tests.conftest import GNMI_AUTH, GNMI_TARGET, requires_live_target


def test_cap(target, is_insecure, tlsconfig):
    response = capabilities(
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
        mode="once",
        timeout=2,
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


@requires_live_target
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

    updates: list[tuple[str, Any]]= [("/system/config/hostname", "minemeow")]
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
