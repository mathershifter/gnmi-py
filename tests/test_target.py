# -*- coding: utf-8 -*-


from gnmi.proto import target_pb2 as pb
from gnmi.models.target import Target, target_factory, _split_addr_port


def test_target_factory():
    tests: list[tuple[Target, pb.Target, bool]] = [
        # (
        #     Target([":6030", "127.0.0.2:6030"]),
        #     pb.Target(addresses=[
        #         "localhost:6030",
        #         "127.0.0.2:6030"
        #     ]),
        #     True
        # ),
        # (
        #     target_factory("unix:///var/run/gnmi.sock"),
        #     pb.Target(addresses=[
        #         "unix:///var/run/gnmi.sock"
        #     ]),
        #     True
        # ),
        # (
        #     Target("localhost"),
        #     pb.Target(addresses=[f"localhost:{IANA_GNMI_PORT}"]),
        #     True
        # ),
        (
            target_factory("localhost:6030"),
            pb.Target(addresses=["localhost:6030"]),
            True,
        ),
        (
            target_factory("cr-1.internal.corp.io:6030"),
            pb.Target(addresses=["cr-1.internal.corp.io:6030"]),
            True,
        ),
        (
            target_factory("127.0.0.1:6030"),
            pb.Target(addresses=["127.0.0.1:6030"]),
            True,
        ),
        (target_factory("[::1]:6030"), pb.Target(addresses=["[::1]:6030"]), True),
        (
            target_factory("[dead:beef::1]:6030"),
            pb.Target(addresses=["[dead:beef::1]:6030"]),
            True,
        ),
    ]

    for test in tests:
        have, want, ok = test
        if ok:
            assert have.encode() == want


def test_split_addr_port():
    tests = [
        (
            ":6030",
            ("", 6030),
        ),
        (
            "cr-1.internal.corp.io",
            ("cr-1.internal.corp.io", 0),
        ),
        (
            "127.0.0.1:6030",
            ("127.0.0.1", 6030),
        ),
        (
            "[::1]:6030",
            ("::1", 6030),
        ),
        (
            "[dead:beef::1]:6030",
            ("dead:beef::1", 6030),
        ),
        (
            "[dead:beef::1]",
            ("dead:beef::1", 0),
        ),
    ]

    for test in tests:
        t, want = test
        got = _split_addr_port(t)
        assert got == want, f"split_addr_port({t!r}) == {got!r}, want {want!r}"
