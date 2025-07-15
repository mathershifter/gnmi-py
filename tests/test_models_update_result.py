# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.update_result import UpdateResult


def test_update_result():
    tests = [
        (
            ("/a/b/c", "replace"),
            pb.UpdateResult(path=pb.Path(elem=[
                pb.PathElem(name='a'),
                pb.PathElem(name='b'),
                pb.PathElem(name='c'),
            ]), op=pb.UpdateResult.Operation.REPLACE),
        )
    ]

    for test in tests:
        have, want = test

        r = UpdateResult(*have)
        assert r.encode() == want