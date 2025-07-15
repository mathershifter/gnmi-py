# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.models import Update
from gnmi.proto import gnmi_pb2 as pb

def test_update():
    tests = [
        (
            Update(path="a/b", value="test"),
            pb.Update(path=pb.Path(elem=[
                pb.PathElem(name="a", key={}),
                pb.PathElem(name="b", key={}),
            ]),
                val=pb.TypedValue(string_val="test")
            ),
        ),
        (
            Update("a/b", {"another": "test"}, 1),
            pb.Update(path=pb.Path(elem=[
                pb.PathElem(name="a", key={}),
                pb.PathElem(name="b", key={}),
            ]),
                val=pb.TypedValue(json_val=b'{"another": "test"}'),
                duplicates=1
            ),
        )
    ]

    for test in tests:
        have, want = test

        assert Update.decode(want) == have
        assert want == have.encode()