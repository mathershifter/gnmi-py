# -*- coding: utf-8 -*-

"""
"""

from dataclasses import dataclass, fields, MISSING
from pathlib import Path
import os

@dataclass
class Env: #(NamedTuple):
    GNMIP_RC_PATH: Path =  Path.home() / ".gnmirc"
    GNMIP_TARGET: str = ""
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

def _load() -> Env:
    s = {}
    for f in fields(Env):
        default = None
        if f.default is not MISSING:
            default = f.default
        
        elif f.default_factory is not MISSING:
            default = f.default_factory()

        val = os.getenv(f.name, default) 
        if val is not None and default is not None:
            val = type(default)(val)
        s[f.name] = val
    return Env(**s)

env = _load()