# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.models.value import Value
from gnmi.proto import gnmi_pb2 as pb

from gnmi.models import Update
from gnmi.models.path import Path

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
            Update(Path.from_str("a/b"), {"another": "test"}, 1),
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
        
        assert isinstance(have.value, Value)
        assert isinstance(have.path, Path)
        assert want == have.encode()
        assert Update.decode(want) == have