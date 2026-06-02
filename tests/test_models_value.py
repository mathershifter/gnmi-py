# -*- coding: utf-8 -*-


from decimal import Decimal

import pytest

from google.protobuf.any_pb2 import Any
from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.value import ValueType, Value, Decimal64


def test_decimal():
    with pytest.warns(DeprecationWarning):
        tests = [
            (
                Decimal("3.14159265359"),
                pb.Decimal64(digits=314159265359, precision=11),
            ),
            # (
            #     Decimal(3.14159265359),
            #     pb.Decimal64(digits=314159265359, precision=11),
            # ),
            (
                Decimal((0, (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 9), -11)),
                pb.Decimal64(digits=314159265359, precision=11),
            ),
        ]

        for test in tests:
            have, want = test
            d = Decimal64(have)
            assert d.precision == want.precision
            assert d.digits == want.digits
            assert d.encode() == want


def test_value_type_from_val_bool():
    assert ValueType.from_val(True) == ValueType.BOOL_VAL
    assert ValueType.from_val(False) == ValueType.BOOL_VAL


def test_value_type_from_val_str():
    assert ValueType.from_val("hello") == ValueType.STRING_VAL


def test_value_type_from_val_int():
    assert ValueType.from_val(42) == ValueType.INT_VAL


def test_value_type_from_val_float():
    assert ValueType.from_val(3.14) == ValueType.FLOAT_VAL


def test_value_type_from_val_bytes():
    assert ValueType.from_val(b"x") == ValueType.BYTES_VAL


def test_value_type_from_val_list():
    assert ValueType.from_val([1, 2]) == ValueType.LEAFLIST_VAL


def test_value_type_from_val_dict():
    assert ValueType.from_val({"a": 1}) == ValueType.JSON_VAL


def test_value_type_from_val_decimal():
    assert ValueType.from_val(Decimal("1.0")) == ValueType.DECIMAL_VAL


def test_value_type_from_val_unknown():
    assert ValueType.from_val(object()) == ValueType.ANY_VAL


def test_value_to_json_string():
    assert Value("hello", ValueType.STRING_VAL).to_json() == "hello"


def test_value_to_json_int():
    assert Value(42, ValueType.INT_VAL).to_json() == 42


def test_value_to_json_float():
    assert Value(3.14, ValueType.FLOAT_VAL).to_json() == 3.14


def test_value_to_json_bool():
    assert Value(True, ValueType.BOOL_VAL).to_json() is True


def test_value_to_json_none():
    assert Value(None, ValueType.ANY_VAL).to_json() is None


def test_value_to_json_bytes():
    assert Value(b"data", ValueType.BYTES_VAL).to_json() == "data"


def test_value_to_json_list():
    v = Value(
        [Value("a", ValueType.STRING_VAL), Value("b", ValueType.STRING_VAL)],
        ValueType.LEAFLIST_VAL,
    )
    assert v.to_json() == ["a", "b"]


def test_value_to_json_decimal():
    assert Value(Decimal("3.14"), ValueType.DECIMAL_VAL).to_json() == 3.14


def test_value_to_json_unsupported_type_raises():
    with pytest.raises(TypeError, match="Unsupported type"):
        Value(object(), ValueType.ANY_VAL).to_json()


def test_value_factory_plain_value():
    from gnmi.models.value import value_factory

    v = value_factory("hello")
    assert v.val == "hello"
    assert v.val_type == ValueType.STRING_VAL


def test_value_factory_passthrough():
    from gnmi.models.value import value_factory

    original = Value(42, ValueType.INT_VAL)
    assert value_factory(original) is original


def test_value_factory_tuple():
    from gnmi.models.value import value_factory

    v = value_factory((True, ValueType.BOOL_VAL))
    assert v.val is True
    assert v.val_type == ValueType.BOOL_VAL


def test_value_factory_invalid_tuple_raises():
    from gnmi.models.value import value_factory

    with pytest.raises((ValueError, TypeError)):
        value_factory((1, 2, 3))


def test_value_json_encoder():
    from gnmi.models.value import ValueJsonEncoder

    enc = ValueJsonEncoder()
    assert enc.default(Value("x", ValueType.STRING_VAL)) == "x"


def test_legacy_value_encode():
    from gnmi.models.value import LegacyValue
    from gnmi.models.encoding import Encoding

    lv = LegacyValue(value=b"data", type=Encoding.JSON)
    encoded = lv.encode()
    assert encoded.value == b"data"


def test_legacy_value_decode():
    from gnmi.models.value import LegacyValue
    from gnmi.models.encoding import Encoding
    pv = pb.Value(value=b"hello", type=0)
    lv = LegacyValue.decode(pv)
    assert lv.value == b"hello"


# ---------------------------------------------------------------------------
# Per-type encode/decode round-trips (T8)
# ---------------------------------------------------------------------------


def test_value_encode_decode_round_trip_int():
    v = Value(42, ValueType.INT_VAL)
    assert Value.decode(v.encode()).val == 42
    assert Value.decode(v.encode()).val_type == ValueType.INT_VAL


def test_value_encode_decode_round_trip_double():
    v = Value(3.14, ValueType.DOUBLE_VAL)
    decoded = Value.decode(v.encode())
    assert abs(decoded.val - 3.14) < 1e-10
    assert decoded.val_type == ValueType.DOUBLE_VAL


def test_value_encode_decode_round_trip_float():
    v = Value(2.5, ValueType.FLOAT_VAL)
    decoded = Value.decode(v.encode())
    assert abs(decoded.val - 2.5) < 1e-5
    assert decoded.val_type == ValueType.FLOAT_VAL


def test_value_encode_decode_round_trip_json():
    v = Value({"key": "val"}, ValueType.JSON_VAL)
    decoded = Value.decode(v.encode())
    assert decoded.val == {"key": "val"}
    assert decoded.val_type == ValueType.JSON_VAL


def test_value_encode_decode_round_trip_json_ietf():
    v = Value({"a": 1}, ValueType.JSON_IETF_VAL)
    decoded = Value.decode(v.encode())
    assert decoded.val == {"a": 1}
    # protobuf json_ietf_val decodes distinctly from json_val
    assert decoded.val_type in (ValueType.JSON_IETF_VAL, ValueType.JSON_VAL)


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------


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
        ),
    ]

    for test in tests:
        have, want = test
        assert Value(*have).encode() == want
