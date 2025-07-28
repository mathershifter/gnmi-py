# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t
from dataclasses import dataclass, field

# from gnmi.models.descriptor import ListDescriptor
from gnmi.proto import gnmi_pb2 as pb
from gnmi.util import escape_string
from gnmi.models.model import BaseModel

PathLike = t.Union[str, "Path", pb.Path]

@dataclass
class PathElem(BaseModel[pb.PathElem]):
    name: str
    key: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        elem = escape_string(self.name, "/")
        for key, val in self.key.items():
            val = escape_string(val, "]")
            elem += "[" + key + "=" + val + "]"
        return elem

    def encode(self) -> pb.PathElem:
        return pb.PathElem(name=self.name, key=self.key)

    @classmethod
    def decode(cls, elem: pb.PathElem) -> "PathElem":
        keys = {}
        for k, v in elem.key.items():
            keys[k] = v

        return cls(
            name=elem.name,
            key=keys,
        )


@dataclass
class Path(BaseModel[pb.Path]):
    elem: list[PathElem]
    origin: str = ""
    target: str = ""

    def __str__(self) -> str:
        elems = []

        for e in self.elem:
            elems.append(str(e))

        path = "/".join(elems)

        if not path.startswith("/"):
            path = "/" + path

        if self.origin:
            path = ":".join([self.origin, path])

        return path

    def is_empty(self):
        return len(self.elem) == 0 and not self.origin  and not self.target

    @classmethod
    def from_str(cls, p: str) -> "Path":
        elems = []
        if not p:
            return cls(elem=[])

        origin, spl = split_path(p)

        for el in spl:
            name, key = parse_elem(el)
            elems.append(PathElem(name=name, key=key))

        return cls(origin=origin, elem=elems)


    def append(self, other: PathLike, force: bool = False) -> "Path":
        other = path_factory(other)

        if not force:
            if other.origin and self.origin != other.origin:
                raise ValueError("Cannot append path with a different origin")

            if other.target and self.target != other.target:
                raise ValueError("Cannot append path with a different targets")

        return Path(
            elem=self.elem + other.elem,
            origin=self.origin,
            target=self.target)


    def __add__(self, other: t.Optional[PathLike]) -> "Path":
        return self.append(other)


    def encode(self) -> pb.Path:
        elem = [e.encode() for e in self.elem]
        return pb.Path(elem=elem, origin=self.origin, target=self.target)


    @classmethod
    def decode(cls, path: pb.Path) -> "Path":
        p: list[PathElem] = []
        for elem in path.elem:
            p.append(PathElem.decode(elem))
        return cls(p, path.origin, path.target)


# class PathDescriptor:
#     def __init__(self, *, default: t.Union[None, str, Path, pb.Path] = None):
#         self._default = None
#
#         if default is not None:
#             self._default = path_factory(default)
#
#
#     def __set_name__(self, owner, name):
#         self._name = "_"+name
#
#
#     def __get__(self, inst, owner):
#         if inst is None:
#             return self._default
#         return getattr(inst, self._name, self._default)
#
#
#     def __set__(self, inst, value: t.Union[Path, str]):
#         setattr(inst, self._name, path_factory(value))


def path_factory(path: t.Optional[PathLike]) -> t.Optional[Path]:
    if path is None:
        return None

    if isinstance(path, Path):
        return path

    if isinstance(path, str):
        return Path.from_str(path)

    if isinstance(path, pb.Path):
        return Path.decode(path)

    raise TypeError(f"Invalid path type {type(path)}")


def split_path(path: str) -> tuple[str, list[str]]:
    origin = ""
    parts: list[str] = []

    buf = ""
    in_key = False
    in_escape = False

    path = path.rstrip("/")

    ch = ""
    for ch in path:
        if ch == '[' and not in_escape:
            in_key = True

        elif ch == ']' and not in_escape:
            in_key = False

        elif ch == '\\' and not in_escape and not in_key:
            in_escape = True
            continue

        elif ch == '/' and not in_escape and not in_key:
            if len(buf) > 0:
                parts.append(buf)
            buf = ""
            continue

        # origin
        if ch == ':' and not in_key and not in_escape:
            origin = buf
            buf = ""
            continue

        buf += ch
        in_escape = False

    if len(buf) != 0 or (len(path) != 1 and ch == '/'):
        parts.append(buf)

    return origin, parts


def parse_elem(elem: str) -> tuple[str, dict[str, str]]:
    el = ""
    keys: dict[str, str] = {}
    buf = ""

    in_key = False
    in_escape = False
    cur = ""

    for ch in elem:
        if ch == '[' and not in_escape and not in_key:
            if not el:
                el = buf
            buf = ""
            in_key = True
            continue
        elif ch == '=' and not in_escape and in_key:
            cur = buf
            buf = ""
            continue

        elif ch == ']' and not in_escape:
            keys[cur] = buf
            buf = ""
            in_key = False
            continue

        elif ch == "\\" and not in_escape:
            in_escape = True
            continue

        buf += ch
        in_escape = False

    if len(buf) > 0:
        el = buf
    return el, keys