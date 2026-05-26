# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Round-trip and error-path coverage for the Subscribe models
(AUDIT.md Testing #4, #10)."""

import pytest

from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.error import Error
from gnmi.models.notification import Notification
from gnmi.models.subscribe import Poll, SubscribeRequest, SubscribeResponse
from gnmi.models.subscription import Subscription
from gnmi.models.subscription_list import SubscriptionList, SubscriptionListMode


def test_subscribe_request_subscribe_round_trip():
    orig = SubscribeRequest(
        subscribe=SubscriptionList(
            subscriptions=[
                Subscription(path="/interfaces/interface[name=Ethernet1]"),
                Subscription(path="/system"),
            ],
            mode=SubscriptionListMode.ONCE,
        )
    )
    decoded = SubscribeRequest.decode(orig.encode())
    assert decoded.subscribe is not None
    assert len(list(decoded.subscribe.subscriptions)) == 2
    assert decoded.subscribe.mode == SubscriptionListMode.ONCE


def test_subscribe_request_poll_round_trip():
    orig = SubscribeRequest(poll=Poll())
    decoded = SubscribeRequest.decode(orig.encode())
    assert decoded.poll is not None


# @pytest.mark.xfail(
#     strict=True,
#     reason="SubscribeRequest.decode reads v.subscribe and v.poll unconditionally; "
#     "protobuf returns default-constructed sub-messages for unset oneof fields, "
#     "so the unset side ends up populated. Should use v.HasField()/WhichOneof().",
# )
def test_subscribe_request_decode_distinguishes_unset_oneof():
    pb_only_poll = SubscribeRequest(poll=Poll()).encode()
    decoded = SubscribeRequest.decode(pb_only_poll)
    assert decoded.subscribe is None


def test_subscribe_request_rejects_both_subscribe_and_poll():
    # The wire format is a oneof — setting both is illegal. encode() must
    # surface that rather than silently dropping one.
    req = SubscribeRequest(
        subscribe=SubscriptionList(subscriptions=[Subscription(path="/a")]),
        poll=Poll(),
    )
    with pytest.raises(ValueError):
        req.encode()


def test_subscribe_request_rejects_neither_subscribe_nor_poll():
    with pytest.raises(ValueError):
        SubscribeRequest().encode()


def test_subscribe_response_update_decode():
    pb_resp = pb.SubscribeResponse(
        update=pb.Notification(
            timestamp=1234,
            update=[
                pb.Update(
                    path=pb.Path(elem=[pb.PathElem(name="a")]),
                    val=pb.TypedValue(string_val="v"),
                )
            ],
        )
    )
    decoded = SubscribeResponse.decode(pb_resp)
    assert decoded.sync_response is False
    assert decoded.error is None
    assert decoded.update.timestamp == 1234
    assert len(decoded.update.updates) == 1


def test_subscribe_response_sync_response_decode():
    decoded = SubscribeResponse.decode(pb.SubscribeResponse(sync_response=True))
    assert decoded.sync_response is True


def test_subscribe_response_error_decode():
    with pytest.warns(DeprecationWarning):
        decoded = SubscribeResponse.decode(
            pb.SubscribeResponse(
                error=pb.Error(code=3, message="boom"),
            )
        )
        assert decoded.error is not None
        assert decoded.error.code == 3
