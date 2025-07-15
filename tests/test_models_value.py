# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from decimal import Decimal
from google.protobuf.any_pb2 import Any

from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.value import ValueType, Value, Decimal64

def test_decimal():
    tests = [
        (
            Decimal("3.14159265359"),
            pb.Decimal64(digits=314159265359, precision=11),
        ),
        (
            3.14159265359,
            pb.Decimal64(digits=314159265359, precision=11),
        ),
        (
            "3.14159265359",
            pb.Decimal64(digits=314159265359, precision=11),
        ),
        (
            (0, (3,1,4,1,5,9,2,6,5,3,5,9), -11),
            pb.Decimal64(digits=314159265359, precision=11),
        )
    ]

    for test in tests:
        have, want = test
        d = Decimal64(have)
        assert d.precision == want.precision
        assert d.digits == want.digits
        assert d.encode() == want

def test_val():
    tests = [
        (
            ("any", ValueType.ANY_VAL),
            pb.TypedValue(any_val=Any(value=b"any")),
        ),
        (
            ("ascii_text", ValueType.ASCII_VAL),
            pb.TypedValue(ascii_val="ascii_text"),
        ),
        (
            (False, ValueType.BOOL_VAL),
            pb.TypedValue(bool_val=False),
        ),
        (
            (b"some_bytes", ValueType.BYTES_VAL),
            pb.TypedValue(bytes_val=b"some_bytes"),
        ),
        (
            (Decimal64(3.14159265359), ValueType.DECIMAL_VAL),
            pb.TypedValue(decimal_val=pb.Decimal64(digits=314159265359, precision=11)),
        ),
        (
            (b"some_proto_bytes", ValueType.PROTO_BYTES),
            pb.TypedValue(proto_bytes=b"some_proto_bytes"),
        ),
        (
            ("string_text", ValueType.STRING_VAL),
            pb.TypedValue(string_val="string_text"),
        ),
        (
            (1000, ValueType.UINT_VAL),
            pb.TypedValue(uint_val=1000),
        )
    ]

    for test in tests:
        have, want = test
        assert Value(*have).encode() == want

