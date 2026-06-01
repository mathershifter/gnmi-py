# -*- coding: utf-8 -*-

from gnmi.models import Path, PathElem, Subscription, SubscriptionMode
from gnmi.proto import gnmi_pb2 as pb


def test_subscription():
    tests = [
        (
            Subscription(
                path=Path(
                    [
                        PathElem("a"),
                        PathElem("b"),
                        PathElem("b"),
                        PathElem("a"),
                    ]
                ),
                mode=SubscriptionMode.TARGET_DEFINED,
            ),
            pb.Subscription(
                path=pb.Path(
                    elem=[
                        pb.PathElem(name="a"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="a"),
                    ]
                ),
                mode=pb.SubscriptionMode.TARGET_DEFINED,
            ),
        ),
        (
            Subscription(path="/a/b/b/a", mode="target_defined"),
            pb.Subscription(
                path=pb.Path(
                    elem=[
                        pb.PathElem(name="a"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="b"),
                        pb.PathElem(name="a"),
                    ]
                ),
                mode=pb.SubscriptionMode.TARGET_DEFINED,
            ),
        ),
    ]

    for test in tests:
        have, want = test
        assert have.encode() == want
        assert Subscription.decode(want) == have
