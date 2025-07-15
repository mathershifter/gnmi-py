# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import typing as t

from dataclasses import fields, is_dataclass


def is_union(typ) -> bool:
    return t.get_origin(typ) is t.Union


def is_optional(typ) -> bool:
    return is_union(typ) and len(t.get_args(typ)) > 0 and (t.get_args(typ)[-1] is type(None))


def unpack_optional(typ) -> t.Any:
    if not is_optional(typ):
        return typ
    return t.get_args(typ)[0]


def deserialize(cls, data: t.Any, omit_none: bool = True) -> t.Any:
    if hasattr(cls, "deserialize"):
        return cls.deserialize(data, flds=fields(cls))

    if isinstance(data, cls) or not is_dataclass(cls):
        return data

    dd = {}
    for fld in fields(cls):
        v: t.Union[t.Iterable, dict, t.Any]
        typ = fld.type
        name = fld.name

        typ = unpack_optional(typ)

        v = data.get(name, None)

        if v is None and omit_none:
            continue

        if m := getattr(cls, f"deserialize_{name}", None):
            v = m(v, fld=fld)

        elif is_dataclass(typ):
            v = deserialize(typ, v)  # type: ignore

        elif t.get_origin(typ) is list:
            v = [deserialize(t.get_args(typ)[0], x) for x in v]

        elif t.get_origin(typ) is dict:
            v = {k: deserialize(t.get_args(typ)[1], x) for k, x in v.items()}

        dd[name] = v

    return cls(**dd)  # type: ignore
