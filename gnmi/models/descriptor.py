# -*- coding: utf-8 -*-

import enum
import datetime
from typing import Generic, TypeVar
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

    def __set__(self, obj, value: datetime.timedelta | int | str):
        if isinstance(value, str):
            value = parse_duration(value)
        elif isinstance(value, datetime.timedelta):
            value = int(value.total_seconds() * 1e9)
        setattr(obj, self._name, int(value))


E = TypeVar("E", bound=enum.Enum)
class Enum(Generic[E]):
    def __init__(self, *, default: E):
        self._default: E = default

    def __set_name__(self, owner, name):\
        self._name = "_" + name


    def __get__(self, obj, typ) -> E:
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)


    def __set__(self, obj, value: str | int | E):
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
