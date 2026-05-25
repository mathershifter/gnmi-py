# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import datetime
import os
import re

import typing as t
import gnmi.proto.gnmi_pb2 as pb # type: ignore

def enable_grpc_debuging():
    os.environ["GRPC_TRACE"] = "all"
    os.environ["GRPC_VERBOSITY"] = "DEBUG"

def constantize(s: str) -> str:
    return s.replace("-", "_").upper()

def get_gnmi_constant(name: str) -> t.Any:
    mode = getattr(pb, constantize(name))
    return mode

def get_datatype(name: str) -> pb.GetRequest.DataType:
    dt: pb.GetRequest.DataType = getattr(pb.GetRequest, constantize(name))
    return dt

def get_subscription_list_mode(name: str) -> pb.SubscriptionList.Mode:
    m: pb.SubscriptionList.Mode = getattr(pb.SubscriptionList, constantize(name))
    return m

_DURATION_MULTIPLIERS = {
    "ns": 1,
    "us": 1_000,
    "ms": 1_000_000,
    "s":  1_000_000_000,
    "m":  60_000_000_000,
}
# "ms" must precede "m"/"s" so the alternation matches the longer unit first.
_DURATION_CHUNK = re.compile(r"(\d+)(ns|us|ms|s|m)?")


def parse_duration(duration: str) -> int:
    """
    Parse a duration string like "100ms", "1s", or "1m30s" into
    nanoseconds. Supported units are ns, us, ms, s, m. A bare number with
    no unit (e.g. "500") is treated as milliseconds.
    """
    if not duration:
        raise ValueError("Empty duration")

    total = 0
    pos = 0
    saw_chunk = False
    for m in _DURATION_CHUNK.finditer(duration):
        if m.start() != pos:
            raise ValueError(f"Invalid duration: {duration!r}")
        unit = m.group(2) or "ms"
        # finditer with the optional unit can return zero-width matches —
        # guard against them by requiring forward progress.
        if m.end() == pos:
            raise ValueError(f"Invalid duration: {duration!r}")
        total += int(m.group(1)) * _DURATION_MULTIPLIERS[unit]
        pos = m.end()
        saw_chunk = True

    if not saw_chunk or pos != len(duration):
        raise ValueError(f"Invalid duration: {duration!r}")

    return total

def prepare_metadata(md: t.Optional[dict[str, t.Any]]) -> list[tuple[str, str]]:
    if md is None:
        return []
    return [(k, str(v)) for k, v in md.items()]

def escape_string(string: str, escape: str) -> str:
    result = ""
    for character in string:
        if character in tuple(escape) + ("\\",):
            result += "\\"
        result += character
    return result

def datetime_from_int64(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp // 1000000000)


def oneof(*args) -> int:
    the=[]

    for i, item in enumerate(args):
        # if item is not None:
        if item is not None and item != False and item != 0:
            the.append(i)

    if len(the) > 1:
        raise ValueError(f"There can only be one; you have {len(the)}")

    if len(the) == 0:
        raise ValueError("There must be one and only be one; you have none")

    return the[0]