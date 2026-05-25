# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from dataclasses import dataclass, field

from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_ext_pb2 as ext_pb2

from gnmi.models.model import BaseModel
from gnmi.models.error import Error
from gnmi.models.notification import Notification
from gnmi.models.subscription_list import SubscriptionList
from gnmi.util import oneof

@dataclass
class Poll(BaseModel[pb.Poll]):

    def encode(self) -> pb.Poll:
        return pb.Poll()

    @classmethod
    def decode(cls, p: pb.Poll) -> "Poll":
        return cls()


@dataclass
class SubscribeRequest(BaseModel[pb.SubscribeRequest]):
    subscribe: SubscriptionList | None = None
    poll: Poll | None = None

    extension: list[ext_pb2.Extension] = field(default_factory=list)

    def encode(self) -> pb.SubscribeRequest:
        sub = None
        poll = None

        idx = oneof(self.subscribe, self.poll)

        if self.subscribe and idx == 0:
            sub = self.subscribe.encode()
        elif self.poll and idx == 1:
            poll = self.poll.encode()
        else:
            raise ValueError("no paths requested for subscribe or poll ")

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
    error: Error | None = None
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
        elif self.error and idx == 2:
            error = self.error.encode()

        return pb.SubscribeResponse(
            update=update,
            sync_response=sync_response or False,
            error=error,
            extension=self.extension,
        )

    @classmethod
    def decode(cls, v: pb.SubscribeResponse) -> "SubscribeResponse":
        err = None
        if v.error and v.error.code != 0:
            err = Error.decode(v.error)
        return cls(
            update=Notification.decode(v.update),
            sync_response=v.sync_response,
            error=err
        )