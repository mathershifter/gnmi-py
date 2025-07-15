# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.set import SetRequest


def test_model_set_request():
    tests = [
        (
            SetRequest(
                prefix="z",
                deletes=["a/b/b/a", "a/c/d/c"]
            ),
            pb.SetRequest(
                prefix=pb.Path(elem=[pb.PathElem(name="z")]),
                delete=[
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
            ),
        )
    ]

    for test in tests:
        want, have = test
        assert want.encode() == have
        assert SetRequest.decode(have) == want

# def test_model_set_response():
#     tests = [
#         (
#             SetResponse(),
#             pb.SetResponse(
#
#             ),
#         )
#     ]
#
#     for test in tests:
#         l, r = test
#         assert l.encode() == r
#         assert SetResponse.decode(r) == l