# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import time

from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.get import GetRequest, GetResponse, DataType
from gnmi.models import Notification

def test_get_request():
    tests = [
        (
            GetRequest(
                prefix="z",
                paths=[
                    "a/b/b/a",
                    "a/c/d/c",
                ],
                type=DataType.ALL,
            ),
            pb.GetRequest(
                prefix=pb.Path(elem=[pb.PathElem(name="z")]),
                path=[
                    pb.Path(elem=[
                        pb.PathElem(name="a"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="a"),
                    ]),
                    pb.Path(elem=[
                        pb.PathElem(name="a"),
                        pb.PathElem(name="c"),
                        pb.PathElem(name="d"),
                        pb.PathElem(name="c"),
                    ])
                ]
            )
        )
    ]

    for test in tests:
        l, r = test

        assert l.encode() == r
        assert GetRequest.decode(r) == l


def test_get_response():
    now = time.time_ns()
    tests = [
        (
            GetResponse(
                notifications=[
                    Notification(
                        timestamp=now,
                        prefix="z",
                        deletes=["a/b"],
                        updates=[
                            ("a/b", "test"),
                            ("a/c", {"another": "test"})
                        ]
                    ),
                ]
            ),
            pb.GetResponse(
                notification=[
                    pb.Notification(
                        timestamp=now,
                        prefix=pb.Path(elem=[pb.PathElem(name="z")]),
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
                ]
            )
        )
    ]

    for test in tests:
        l, r = test

        assert l.encode() == r
        assert GetResponse.decode(r) == l