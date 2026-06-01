# -*- coding: utf-8 -*-

from typing import TypeAlias, Sequence

from dataclasses import dataclass, field

from gnmi.proto import gnmi_pb2 as pb
from gnmi.util import escape_string
from gnmi.models.model import BaseModel


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
    def decode(cls, v: pb.PathElem) -> "PathElem":
        keys = {}
        for k, val in v.key.items():
            keys[k] = val

        return cls(
            name=v.name,
            key=keys,
        )


@dataclass
class Path(BaseModel[pb.Path]):
    """A gNMI path.

    A sequence of :class:`PathElem` (each a name plus optional key map),
    plus an optional ``origin`` (e.g. ``openconfig``) and ``target``.
    Construct from a string with :meth:`Path.from_str` or by passing one
    to ``path_factory`` / any descriptor field that accepts ``PathLike``.
    Stringification is lossless: ``Path.from_str(str(p)) == p``.
    """

    elem: Sequence[PathElem]
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

    def __truediv__(self, scalar):
        return self.__add__(scalar)

    def __add__(self, scalar):
        right = path_factory(scalar)
        return self.append(right)

    def is_empty(self):
        return len(self.elem) == 0 and not self.origin and not self.target

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

    def append(self, other: "str | Path | pb.Path", force: bool = False) -> "Path":
        other = path_factory(other)

        if not force:
            if other.origin and self.origin != other.origin:
                raise ValueError("Cannot append path with a different origin")

            if other.target and self.target != other.target:
                raise ValueError("Cannot append path with a different targets")

        return Path(
            elem=list(self.elem) + list(other.elem),
            origin=self.origin,
            target=self.target,
        )

    def encode(self) -> pb.Path:
        elem = [e.encode() for e in self.elem]
        if not self.origin and not self.target and len(elem) == 0:
            return pb.Path()
        return pb.Path(elem=elem, origin=self.origin, target=self.target)

    @classmethod
    def decode(cls, v: pb.Path) -> "Path":
        p: list[PathElem] = []
        for elem in v.elem:
            p.append(PathElem.decode(elem))

        if not v.origin and not v.target:
            return cls(elem=p)

        return cls(p, v.origin, v.target)


PathLike: TypeAlias = str | Path | pb.Path


class PathDescriptor:
    def __init__(self, *, default: None | PathLike = None):
        self._default = None
        if default is not None:
            self._default = path_factory(default)

    def __set_name__(self, _, name):
        self._name = "_" + name

    def __get__(self, inst, _):
        if inst is None:
            return self._default
        return getattr(inst, self._name, self._default)

    def __set__(self, inst, value: None | PathLike):
        if value is None:
            return None
        setattr(inst, self._name, path_factory(value))


class Paths:
    def __set_name__(self, _, name):
        self._name = "_" + name

    def __get__(self, inst, _):
        return getattr(inst, self._name, [])

    def __set__(self, inst, value: Sequence[PathLike]):
        # See Subscriptions.__set__ — handle dataclass-default round-trip.
        if value is self:
            return
        if not value:
            return
        setattr(inst, self._name, [path_factory(p) for p in value])


def path_factory(path: PathLike) -> Path:
    if isinstance(path, Path):
        return path

    if isinstance(path, str):
        return Path.from_str(path)

    if isinstance(path, pb.Path):
        return Path.decode(path)

    raise TypeError(f"Invalid path type {type(path)}")


def split_path(path: str) -> tuple[str, list[str]]:
    """Slice an escaped path into (target, origin, [elements]).

    This is a *separator-only* pass: it respects escape sequences so that
    `\\/`, `\\[`, `\\:` aren't treated as separators, but it preserves the
    backslash in the output. `parse_elem` does the actual unescape.
    """
    origin = ""
    parts: list[str] = []

    buf = ""
    in_key = False
    in_escape = False

    path = path.rstrip("/")

    ch = ""
    for ch in path:
        if in_escape:
            # Previous char was a backslash escape — pass this one through
            # untouched so the element parser can still see the escape.
            buf += ch
            in_escape = False
            continue

        if ch == "\\" and not in_key:
            in_escape = True
            buf += ch
            continue

        if ch == "[":
            in_key = True
        elif ch == "]":
            in_key = False
        elif ch == "/" and not in_key:
            if len(buf) > 0:
                parts.append(buf)
            buf = ""
            continue
        elif ch == ":" and not in_key:
            if len(buf) > 0:
                if not origin:
                    origin = buf
                else:
                    raise ValueError(f"Invalid path: too many ':' separators: {path}")
            buf = ""
            continue

        buf += ch

    if len(buf) != 0 or (len(path) != 1 and ch == "/"):
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
        if ch == "[" and not in_escape and not in_key:
            if not el:
                el = buf
            buf = ""
            in_key = True
            continue
        elif ch == "=" and not in_escape and in_key:
            cur = buf
            buf = ""
            continue

        elif ch == "]" and not in_escape:
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
