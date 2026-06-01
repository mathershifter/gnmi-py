# -*- coding: utf-8 -*-

from gnmi.proto import gnmi_pb2 as pb

from gnmi.models.set import SetRequest, SetResponse
from gnmi.models.update_result import UpdateResult, Operation


def test_model_set_request():
    tests = [
        (
            SetRequest(prefix="z", deletes=["a/b/b/a", "a/c/d/c"]),
            pb.SetRequest(
                prefix=pb.Path(elem=[pb.PathElem(name="z")]),
                delete=[
                    pb.Path(
                        elem=[
                            pb.PathElem(name="a"),
                            pb.PathElem(name="b"),
                            pb.PathElem(name="b"),
                            pb.PathElem(name="a"),
                        ]
                    ),
                    pb.Path(
                        elem=[
                            pb.PathElem(name="a"),
                            pb.PathElem(name="c"),
                            pb.PathElem(name="d"),
                            pb.PathElem(name="c"),
                        ]
                    ),
                ],
            ),
        )
    ]

    for test in tests:
        want, have = test
        assert want.encode() == have
        assert SetRequest.decode(have) == want


def test_model_set_response_round_trip():
    resp = SetResponse(
        prefix="/system",
        responses=[
            UpdateResult(path="/config/hostname", op=Operation.UPDATE),
            UpdateResult(path="/state/stale", op=Operation.DELETE),
        ],
        timestamp=99,
    )
    encoded = resp.encode()
    assert encoded.timestamp == 99
    assert len(encoded.response) == 2

    decoded = SetResponse.decode(encoded)
    assert decoded.timestamp == 99
    assert [r.op.name for r in decoded.responses] == ["UPDATE", "DELETE"]


def test_model_set_response_decode_empty():
    decoded = SetResponse.decode(pb.SetResponse())
    assert decoded.responses == []
    assert decoded.message is None
