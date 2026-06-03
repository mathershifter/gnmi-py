# -*- coding: utf-8 -*-

""" """

import re
from dataclasses import dataclass, fields, field, MISSING
from pathlib import Path
import os


@dataclass
class Env:
    GNMIP_RC_PATH: list[Path] = field(default_factory=lambda: [Path.home() / ".gnmirc"])
    GNMIP_TARGET: list[str] = field(default_factory=list)
    GNMIP_USER: str = "admin"
    GNMIP_PASS: str = ""
    GNMIP_NO_DEPRECATED: bool = False
    GNMIP_DEBUG_GRPC: bool = False
    GNMIP_INSECURE: bool = False
    GNMIP_HOST_OVERRIDE: str = ""
    GNMIP_TLS_GET_TARGET_CERTIFICATE: bool = False
    GNMIP_TLS_CA: str = ""
    GNMIP_TLS_CERT: str = ""
    GNMIP_TLS_KEY: str = ""
    GNMIP_TLS_NO_VERIFY: bool = False
    GNMIP_FORMAT: str = "pretty"


def _coerce_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("yes", "true", "t", "1")
    return bool(val)


def _coerce_list(val, default: list[str] = []):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        typ = type(default[0]) if default else str
        return [
            _coerce_type(v.strip(), typ) for v in re.split(r"[,|:]", val) if v.strip()
        ]
    return list(val)


def _coerce_type(val, typ: type):
    if typ is bool:
        return _coerce_bool(val)
    elif typ is list:
        return _coerce_list(val)
    elif val is not None and typ is not None:
        return typ(val)
    return val


def _load() -> Env:
    s = {}
    for f in fields(Env):
        default = None
        if f.default is not MISSING:
            default = f.default

        elif f.default_factory is not MISSING:
            default = f.default_factory()

        val = os.getenv(f.name, default)
        val = _coerce_type(val, type(default))

        s[f.name] = val

    return Env(**s)


env = _load()
