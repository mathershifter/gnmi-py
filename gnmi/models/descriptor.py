# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import enum
import datetime
import typing as t
from gnmi.util import parse_duration

class Duration:
    def __init__(self, *, default: int = 0):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, typ):
        if obj is None:
            return self._default

        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value: t.Union[datetime.timedelta, int, str]):
        if isinstance(value, str):
            value = parse_duration(value)

        setattr(obj, self._name, int(value))


E = t.TypeVar("E", bound=enum.Enum)
class Enum(t.Generic[E]):
    def __init__(self, *, default: E):
        self._default: E = default

    def __set_name__(self, owner, name):\
        self._name = "_" + name


    def __get__(self, obj, typ) -> E:
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)


    def __set__(self, obj, value: t.Union[str, int, E]):
        cls = getattr(obj, self._name, self._default).__class__

        if isinstance(value, cls):
            setattr(obj, self._name, value)
        elif isinstance(value, str):
            value = value.replace("-", "_").upper()
            setattr(obj, self._name, cls[value])
        elif isinstance(value, int):
            setattr(obj, self._name, cls(value))
        else:
            raise TypeError(f"'{value}' is not a valid enum value")


# class ListDescriptor(TypedDescriptor[T]):
#     def __init__(self, *, factory: type[list[str], list[T]]):
#         self._factory = factory
#
#     def __set_name__(self, owner, name):
#         self._name = "_" + name
#
#     def __get__(self, obj, typ) -> t.Callable[[], list[T]]:
#         if obj is None:
#             return list[T]
#
#         return getattr(obj, self._name, self._factory)
#
#     def __set__(self, obj, value: list):
#         setattr(obj, self._name, self._factory(value))