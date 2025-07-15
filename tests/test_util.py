# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.util import parse_duration

def test_parse_duration():
    tests = {
        "1ns": 1,
        "1us": 1000,
        "1ms": 1_000_000,
        "1s": 1_000_000_000,
        "1m": 60_000_000_000,
        "1586ms": 1_586_000_000
    }
    for s, want in tests.items():
        got = parse_duration(s)
        assert got == want
