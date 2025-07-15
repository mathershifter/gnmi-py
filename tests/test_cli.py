# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.cli import parse_args, arg_loader
from gnmi import config
# from pprint import pprint
def test_arg_loader():
    tests = [
        (
            [
                "ceos1:6030", "capabilities"
            ],
            config.Config(
                target="ceos1:6030",
                capabilities=config.Capabilities()
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
            config.Config(
                target="ceos1:6030",
                get=config.Get(
                    paths=[
                        "interface[name=Ethernet3/1/1]/state/counters",
                        "interface[name=Ethernet3/2/1.1000]/state/counters"
                    ],
                    prefix="/interfaces",
                    type=config.DataType.ALL,
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
        
            config.Config(
                target="ceos1:6030",
                subscribe=config.Subscribe(
                    
                    subscriptions=[
                        config.Subscription(
                            path="interface/state/counters",
                            mode=config.SubscriptionMode.ON_CHANGE,
                            # heartbeat_interval=10*1_000_000_000
                        ),
                    ],
                    prefix="/interfaces",
                    mode=config.SubscribeMode.ONCE
                )
            )
        )
    ]
    
    for t in tests:
        args, want = t
        cnf = config.load(arg_loader, parse_args(args))
        assert cnf == want


