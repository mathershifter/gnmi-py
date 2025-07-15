# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t

from dataclasses import dataclass, field

from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2
from gnmi.models.model import BaseModel
from gnmi.models.error import Error
from gnmi.models.notification import Notification
from gnmi.models.subscription_list import SubscriptionList
from gnmi.proto.gnmi_pb2 import Poll
from gnmi.util import oneof

@dataclass
class Poll(BaseModel[pb.Poll]):

    def encode(self) -> pb.Poll:
        return pb.Poll()

    @classmethod
    def decode(cls, p: pb.Poll) -> Poll:
        return cls()


@dataclass
class SubscribeRequest(BaseModel[pb.SubscribeRequest]):
    subscribe: t.Optional[SubscriptionList] = None
    poll: t.Optional[Poll] = None

    extension: list[ext_pb2.Extension] = field(default_factory=list)

    def encode(self) -> pb.SubscribeRequest:
        sub = None
        poll = None

        idx = oneof(self.subscribe, self.poll)

        if idx == 0:
            sub = self.subscribe.encode()

        if idx == 1:
            poll = self.poll.encode()

        return pb.SubscribeRequest(
            subscribe=sub,
            poll=poll,
            extension=self.extension,
        )

    @classmethod
    def decode(cls, v: pb.SubscribeRequest) -> 'SubscribeRequest':
        sub = None
        poll = None

        return cls(
            subscribe=sub,
            poll=poll,
            extension=list(v.extension)
        )


@dataclass
class SubscribeResponse(BaseModel[pb.SubscribeResponse]):
    update: Notification
    sync_response: bool
    error: t.Optional[Error] = None
    extension: list[ext_pb2.Extension] = field(default_factory=list)

    def encode(self) -> pb.SubscribeResponse:
        update = None
        sync_response = None
        error = None

        idx = oneof(self.update, self.sync_response, self.error)

        if idx == 0:
            update = self.update.encode()
        elif idx == 1:
            sync_response = self.sync_response
        elif idx == 2:
            error = self.error.encode()

        return pb.SubscribeResponse(
            update=update,
            sync_response=sync_response,
            error=error,
            extension=self.extension,
        )

    @classmethod
    def decode(cls, v: pb.SubscribeResponse) -> "SubscribeResponse":
        err = None
        if v.error is not None:
            err = Error.decode(v.error)

        return cls(
            update=Notification.decode(v.update),
            sync_response=v.sync_response,
            error=err
        )