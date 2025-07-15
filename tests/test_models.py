# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from gnmi.models import Subscription
from gnmi.proto import gnmi_pb2 as pb

from gnmi import models

def test_subscription_list_mode():
    tests = [
        (
            models.SubscriptionListMode.from_str("STREAM"),
            pb.SubscriptionList.Mode.STREAM
        ),
    ]

    for t in tests:
        mode, want = t
        assert mode.value == want

def test_subscription_list():
    tests = [
        (
            models.SubscriptionList(
                prefix="interfaces",
                subscriptions=[
                    models.Subscription(
                        path="interface[name=Ethernet1/2/3]/state/counters",
                        mode="on-change",
                        heartbeat_interval="1s",
                    ),
                ],
                encoding="json",
                mode="stream",
            ),
            pb.SubscriptionList(
                prefix=pb.Path(elem=[
                    pb.PathElem(name="interfaces")
                ]),
                subscription=[
                    pb.Subscription(
                        path = pb.Path(elem=[
                            pb.PathElem(name="interface", key={"name": "Ethernet1/2/3"}),
                            pb.PathElem(name="state"),
                            pb.PathElem(name="counters"),
                        ]),
                        mode = pb.SubscriptionMode.ON_CHANGE,
                        heartbeat_interval = 1_000_000_000
                    )
                ],
                encoding=pb.Encoding.JSON,
                mode=pb.SubscriptionList.Mode.STREAM,
                qos=pb.QOSMarking(marking=0),
            )
        ),
    ]

    for t in tests:
        sub, want = t
        assert sub.encode() == want

def test_subscription():
    tests = [
        (
            models.Subscription(
                path="openconfig:interfaces/interface[name=Ethernet1/2/3]/state/counters",
                mode="on-change",
                sample_interval="1s",
            ),
            pb.Subscription(
                path = pb.Path(elem=[
                    pb.PathElem(name="interfaces"),
                    pb.PathElem(name="interface", key={"name": "Ethernet1/2/3"}),
                    pb.PathElem(name="state"),
                    pb.PathElem(name="counters"),
                ], origin="openconfig"),
                mode = pb.SubscriptionMode.ON_CHANGE,
                sample_interval=1_000_000_000
            )
        )
    ]

    for t in tests:
        sub, want = t
        assert sub.encode() == want
        assert Subscription.decode(want) == sub
