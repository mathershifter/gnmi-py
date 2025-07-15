# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.subscribe import SubscribeRequest

# def test_subscribe_request():
#     tests = [
#         (
#             SubscribeRequest(),
#             pb.SubscribeRequest()
#         )
#     ]
#
#     for test in tests:
#         l, r = test
#
#         assert l.encode() == r
#         assert SubscribeRequest.decode(r) == l
