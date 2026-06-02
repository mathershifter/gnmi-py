# -*- coding: utf-8 -*-

from unittest import mock

import grpc

from gnmi.models.status import Status


def test_status_fields():
    s = Status(code=grpc.StatusCode.OK, details="fine", trailing_metadata=[])
    assert s.code == grpc.StatusCode.OK
    assert s.details == "fine"
    assert s.trailing_metadata == []


def test_status_from_call():
    call = mock.MagicMock()
    call.code.return_value = grpc.StatusCode.NOT_FOUND
    call.details.return_value = "missing"
    call.trailing_metadata.return_value = [("k", "v")]

    s = Status.from_call(call)
    assert s.code == grpc.StatusCode.NOT_FOUND
    assert s.details == "missing"
    assert s.trailing_metadata == [("k", "v")]
