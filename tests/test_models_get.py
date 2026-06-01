# -*- coding: utf-8 -*-

import time

from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.get import GetRequest, GetResponse, DataType
from gnmi.models.update import update_factory
from gnmi.models.path import Path
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
                    pb.Path(
                        elem=[
                            pb.PathElem(name="a"),
                            pb.PathElem(name="b"),
                            pb.PathElem(name="b"),
                            pb.PathElem(name="a"),
                        ]
                    ),
                    pb.Path(
                        elem=[
                            pb.PathElem(name="a"),
                            pb.PathElem(name="c"),
                            pb.PathElem(name="d"),
                            pb.PathElem(name="c"),
                        ]
                    ),
                ],
            ),
        )
    ]

    for test in tests:
        want, have = test

        assert want.encode() == have
        assert GetRequest.decode(have) == want


def test_get_response():
    now = time.time_ns()
    tests = [
        (
            GetResponse(
                notifications=[
                    Notification(
                        timestamp=now,
                        prefix=Path.from_str("z"),
                        deletes=[Path.from_str(p) for p in ["a/b"]],
                        updates=[
                            update_factory(u)
                            for u in [("a/b", "test"), ("a/c", {"another": "test"})]
                        ],
                    ),
                ]
            ),
            pb.GetResponse(
                notification=[
                    pb.Notification(
                        timestamp=now,
                        prefix=pb.Path(elem=[pb.PathElem(name="z")]),
                        delete=[
                            pb.Path(elem=[pb.PathElem(name="a"), pb.PathElem(name="b")])
                        ],
                        update=[
                            pb.Update(
                                path=pb.Path(
                                    elem=[
                                        pb.PathElem(name="a", key={}),
                                        pb.PathElem(name="b", key={}),
                                    ]
                                ),
                                val=pb.TypedValue(string_val="test"),
                            ),
                            pb.Update(
                                path=pb.Path(
                                    elem=[
                                        pb.PathElem(name="a", key={}),
                                        pb.PathElem(name="c", key={}),
                                    ]
                                ),
                                val=pb.TypedValue(json_val=b'{"another": "test"}'),
                            ),
                        ],
                    )
                ]
            ),
        )
    ]

    for test in tests:
        want, have = test

        assert want.encode() == have
        decoded = GetResponse.decode(have)
        assert len(decoded.notifications) == len(want.notifications)
        for got_n, want_n in zip(decoded.notifications, want.notifications):
            assert got_n.timestamp == want_n.timestamp
            assert len(got_n.updates) == len(want_n.updates)


def test_get_request_data_type_round_trip():
    # Each DataType variant must survive encode → decode.
    for dt in DataType:
        req = GetRequest(paths=["/a"], type=dt)
        decoded = GetRequest.decode(req.encode())
        assert decoded.type == dt
