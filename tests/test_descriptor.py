# -*- coding: utf-8 -*-

import enum
from dataclasses import dataclass

from gnmi.models.descriptor import Enum  # EnumDescriptor, ListDescriptor


def test_enum_descriptor():
    class TestEnum(enum.Enum):
        A = 0
        B = 1
        C = 2

    @dataclass
    class TestEnumDescriptor:
        value: Enum[TestEnum] = Enum(default=TestEnum.A)

    t = TestEnumDescriptor(value="B")
    assert t.value == TestEnum.B

    t = TestEnumDescriptor(value=2)
    assert t.value == TestEnum.C

    t = TestEnumDescriptor(value=TestEnum.B)
    assert t.value == TestEnum.B


def test_enum_descriptor_invalid_type_raises():
    class TestEnum(enum.Enum):
        A = 0

    @dataclass
    class TestEnumDescriptor:
        value: Enum[TestEnum] = Enum(default=TestEnum.A)

    import pytest

    with pytest.raises(TypeError):
        TestEnumDescriptor(value=3.14)


def test_duration_descriptor_with_timedelta():
    import datetime
    from gnmi.models.descriptor import Duration

    @dataclass
    class Timed:
        dur: Duration = Duration(default=0)

    t = Timed(dur=datetime.timedelta(seconds=5))
    assert t.dur == 5_000_000_000


def test_duration_descriptor_with_string():
    from gnmi.models.descriptor import Duration

    @dataclass
    class Timed:
        dur: Duration = Duration(default=0)

    t = Timed(dur="1s")
    assert t.dur == 1_000_000_000


def test_duration_descriptor_with_int():
    from gnmi.models.descriptor import Duration

    @dataclass
    class Timed:
        dur: Duration = Duration(default=0)

    t = Timed(dur=500)
    assert t.dur == 500


def test_data_type_descriptor_with_string():
    from gnmi.models.get import DataType, GetRequest

    gr = GetRequest(paths=["/a"], type="config")
    assert gr.type == DataType.CONFIG


def test_data_type_descriptor_invalid_string_raises():
    from gnmi.models.get import GetRequest
    import pytest

    with pytest.raises(TypeError, match="invalid data type"):
        GetRequest(paths=["/a"], type="bogus")


# def test_listof_descriptors():
#     class TestEnum(enum.Enum):
#         A = 0
#         B = 1
#         C = 2
#
#     @dataclass
#     class Token:
#         token: list[str]
#
#     @dataclass
#     class TestListOfDescriptor:
#         updates: ListDescriptor = ListDescriptor[Path](
#             factory=lambda l: [Path.from_str(p) for p in l]
#         )
#
#     t = TestListOfDescriptor(updates=["a/b/b/a", "a/c/d/c"])
#     # print(f"UPDATES: {t.updates}")
#     assert t.updates == [Path.from_str("a/b/b/a"), Path.from_str("a/c/d/c")]
