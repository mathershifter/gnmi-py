# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import datetime
import os
import re
import pathlib

import typing as t
import gnmi.proto.gnmi_pb2 as pb # type: ignore

from gnmi.environments import GNMI_RC_PATH
from gnmi.config import Config
from gnmi.constants import GNMIRC_FILES

RE_PATH_COMPONENT = re.compile(
    r"""
^
(?P<name>[^[]+)
(?P<keyval>\[.*\])?$
""",
    re.VERBOSE,
)


def enable_grpc_debuging():
    os.environ["GRPC_TRACE"] = "all"
    os.environ["GRPC_VERBOSITY"] = "DEBUG"


def get_gnmi_constant(name: str) -> t.Any: #pb.SubscriptionMode:
    mode = getattr(pb, name.replace("-", "_").upper())
    return mode


def load_rc() -> Config:
    rc = Config({})
    path = pathlib.Path(GNMI_RC_PATH)
    for name in GNMIRC_FILES:
        fil = path / name
        if fil.exists():
            rc = Config.load_file(fil)
            break
    
    return rc


def parse_duration(duration: str) -> t.Optional[int]:
    multipliers = {"n": 1, "u": 1000, "m": 1000000, "ms": 1000000, "s": 1000000000}

    if duration is None:
        return None

    match = re.match(r"(?P<value>\d+)(?P<unit>[a-z]+)?", duration)
    if match is None:
        return None

    val = int(match.group("value"))
    unit = match.group("unit") or "m"

    if unit not in multipliers:
        raise ValueError("Invalid unit in duration: %s" % duration)

    return val * multipliers[unit]


def parse_path(path: str) -> list[dict[str, t.Any]]:
    parsed = []
    elems = [re.sub(r"\\", "", name) for name in re.split(r"(?<!\\)/", path) if name]

    for elem in elems:
        keys = {}
        match = RE_PATH_COMPONENT.search(elem)
        if match is None:
            continue
        name = match.group("name")
        keyvals = match.group("keyval")
        if keyvals:
            for keyval in re.findall(r"\[([^]]*)\]", keyvals):
                key, val = keyval.split("=")
                keys[key] = val

        parsed.append(dict(name=name, keys=keys))

    return parsed


def prepare_metadata(data: dict[str, t.Any]) -> list[tuple[str, str]]:
    # normailize metadata to a list of tuples
    # ndata = []
    # for key, val in data.items():
    #     ndata.append((key, str(val)))
    
    return [(k, str(v)) for k, v in data.items()]


def escape_string(string: str, escape: str) -> str:
    result = ""
    for character in string:
        if character in tuple(escape) + ("\\",):
            result += "\\"
        result += character
    return result


def datetime_from_int64(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp // 1000000000)
