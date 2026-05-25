# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.cli import parse_args, arg_loader
from gnmi.config import Config, Capabilities, Get, Subscription, Subscribe

def test_arg_loader():
    tests = [
        (
            [
                "ceos1:6030", "capabilities"
            ],
            Config(
                target="ceos1:6030",
                capabilities=Capabilities()
            )
        ),
        (
            [
                "--prefix", "/interfaces",
                "--get-type", "all",
                "--encoding", "json",
                "ceos1:6030", "get",
                "interface[name=Ethernet3/1/1]/state/counters",
                "interface[name=Ethernet3/2/1.1000]/state/counters",
            ],
            Config(
                target="ceos1:6030",
                get=Get(
                    paths=[
                        "interface[name=Ethernet3/1/1]/state/counters",
                        "interface[name=Ethernet3/2/1.1000]/state/counters"
                    ],
                    prefix="/interfaces",
                    type="all",
                ),
            )
        ),
        (
            [
                "--qos", "0",
                "--mode", "once",
                "--submode", "on-change",
                "--encoding", "json",
                # "--heartbeat", "10s",
                "--prefix", "/interfaces",
                "ceos1:6030", "subscribe",
                "interface/state/counters",
            ],
        
            Config(
                target="ceos1:6030",
                subscribe=Subscribe(
                    
                    subscriptions=[
                        Subscription(
                            path="interface/state/counters",
                            mode="on-change",
                            # heartbeat_interval=10*1_000_000_000
                        ),
                    ],
                    prefix="/interfaces",
                    mode="once"
                )
            )
        )
    ]
    
    for t in tests:
        args, want = t
        cnf = Config(**arg_loader(parse_args(args)))  # type: ignore
        assert cnf == want


