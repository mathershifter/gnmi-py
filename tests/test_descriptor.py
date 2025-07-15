# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
from dataclasses import dataclass

from gnmi.models.descriptor import Enum #EnumDescriptor, ListDescriptor

def  test_enum_descriptor():
    class TestEnum(enum.Enum):
        A = 0
        B = 1
        C = 2

    @dataclass
    class TestEnumDescriptor:
        value: Enum[TestEnum] = Enum(default=TestEnum.A)

    t = TestEnumDescriptor(value='B')
    assert t.value == TestEnum.B

    t = TestEnumDescriptor(value=2)
    assert t.value == TestEnum.C

    t = TestEnumDescriptor(value=TestEnum.B)
    assert t.value == TestEnum.B


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
