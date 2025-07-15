# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import datetime
import os

import typing as t
import gnmi.proto.gnmi_pb2 as pb # type: ignore

def enable_grpc_debuging():
    os.environ["GRPC_TRACE"] = "all"
    os.environ["GRPC_VERBOSITY"] = "DEBUG"

def contstantize(s: str) -> str:
    return s.replace("-", "_").upper()

def get_gnmi_constant(name: str) -> t.Any:
    mode = getattr(pb, contstantize(name))
    return mode

def get_datatype(name: str) -> pb.GetRequest.DataType:
    dt: pb.GetRequest.DataType = getattr(pb.GetRequest, contstantize(name))
    return dt

def get_subscription_list_mode(name: str) -> pb.SubscriptionList.Mode:
    m: pb.SubscriptionList.Mode = getattr(pb.SubscriptionList, contstantize(name))
    return m

def parse_duration(duration: str) -> int:
    multipliers = {
        "ns": 1,
        "us": 1000,
        "ms": 1_000_000,
        "s": 1_000_000_000,
        "m": 60_000_000_000
    }

    buf = ""
    val = 0
    unit = "ms"
    in_val = False
    in_unit = False

    for ch in duration:
        if ch.isdigit():
            buf += ch
            in_val = True
            continue
        if ch.isalpha():
            if in_val:
                val = int(buf)
                buf = ""
                in_val = False
                in_unit = True
            buf += ch
    
    if len(buf) > 0 and val > 0:
        if in_unit:
            unit = buf
        elif in_val:
            val = int(buf)

    if unit not in multipliers:
        raise ValueError("Invalid unit in duration: %s" % duration)

    return val * multipliers[unit]

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
        if item is not None:
            the.append(i)

    if len(the) > 1:
        raise ValueError(f"There can only be one; you have {len(the)}")

    if len(the) == 0:
        raise ValueError("There must be one and only be one; you have none")

    return the[0]