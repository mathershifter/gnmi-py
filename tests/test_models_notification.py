# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import time
from gnmi.models import Notification
# from gnmi.models.path import PathDescriptor
from gnmi.proto import gnmi_pb2 as pb

def test_notification():
    now = time.time_ns()
    tests = [
        (
            Notification(
                timestamp=now,
                prefix="z",
                deletes=["a/b"],
                updates=[
                    ("a/b", "test"),
                    ("a/c", {"another": "test"})
                ]
            ),
            pb.Notification(
                timestamp=now,
                prefix=pb.Path(elem=[pb.PathElem(name="z", key={})]),
                delete=[
                    pb.Path(elem=[
                        pb.PathElem(name="a"),
                        pb.PathElem(name="b")
                    ])
                ],
                update=[
                    pb.Update(
                        path=pb.Path(elem=[
                            pb.PathElem(name="a", key={}),
                            pb.PathElem(name="b", key={}),
                        ]),
                        val=pb.TypedValue(string_val="test"),
                    ),
                    pb.Update(
                        path=pb.Path(elem=[
                            pb.PathElem(name="a", key={}),
                            pb.PathElem(name="c", key={}),
                        ]),
                        val=pb.TypedValue(json_val=b'{"another": "test"}'),
                    )
                ]
            )
        ),
        (
            Notification(
                timestamp=now,
                updates=[],
                deletes=[
                    "/interfaces/interface[name=Ethernet1]",
                ]
            ),
            pb.Notification(
                timestamp=now,
                delete=[
                    pb.Path(elem=[
                        pb.PathElem(name="interfaces", key={}),
                        pb.PathElem(name="interface", key={"name": "Ethernet1"}),
                    ])
                ],
            ),
        ),
        (
            Notification(
                timestamp=now,
                prefix="/interfaces",
                updates=[],
                deletes=[
                    "interface[name=Ethernet1]",
                ]
            ),
            pb.Notification(
                timestamp=now,
                prefix=pb.Path(elem=[
                    pb.PathElem(name="interfaces", key={}),
                ]),
                # update=[],
                delete=[
                    pb.Path(elem=[
                        pb.PathElem(name="interface", key={"name": "Ethernet1"}),
                    ])
                ],
            ),
        )
    ]

    for test in tests:
        notif, want = test
        # print(f"NOTIF: {notif}")
        assert notif.encode() == want
        assert Notification.decode(want) == notif