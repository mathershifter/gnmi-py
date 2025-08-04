# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.proto import target_pb2 as pb
from gnmi.models.target import Target

def test_target():
    tests: list[tuple[Target, pb.Target, bool]] = [
        # (
        #     Target([":6030", "127.0.0.2:6030"]),
        #     pb.Target(addresses=[
        #         "localhost:6030",
        #         "127.0.0.2:6030"
        #     ]),
        #     True
        # ),
        (
            Target("unix:///var/run/gnmi.sock"),
            pb.Target(addresses=[
                "unix:///var/run/gnmi.sock"
            ]),
            True
        ),
        (
            Target("localhost:6030"),
            pb.Target(addresses=[
                "localhost:6030"
            ]),
            True
        ),
        # (
        #     Target("localhost"),
        #     pb.Target(addresses=[f"localhost:{IANA_GNMI_PORT}"]),
        #     True
        # ),
        (
            Target("cr-1.internal.corp.io:6030"),
            pb.Target(addresses=["cr-1.internal.corp.io:6030"]),
            True
        ),
        (
            Target("127.0.0.1:6030"),
            pb.Target(addresses=["127.0.0.1:6030"]),
            True
        ),
        (
            Target("[::1]:6030"),
            pb.Target(addresses=["[::1]:6030"]),
            True
        ),
        (
            Target("[dead:beef::1]:6030"),
            pb.Target(addresses=["[dead:beef::1]:6030"]),
            True
        )
    ]

    for test in tests:
        have, want, ok = test
        if ok:
            assert have.encode() == want
#
# def test_split_addr_port():
#     tests = [
#         (
#             ":6030",
#             ("", 6030),
#         ),
#         (
#             "cr-1.internal.corp.io",
#             ("cr-1.internal.corp.io", 0),
#         ),
#         (
#             "127.0.0.1:6030",
#             ("127.0.0.1", 6030),
#         ),
#         (
#             "[::1]:6030",
#             ("::1", 6030),
#         ),
#         (
#             "[dead:beef::1]:6030",
#             ("dead:beef::1", 6030),
#         ),
#         (
#             "[dead:beef::1]",
#             ("dead:beef::1", 0),
#         ),
#     ]
#
#     for test in tests:
#         t, want = test
#
#         assert split_addr_port(t) == want