# -*- coding: utf-8 -*-

from gnmi.models.configuration import Configuration
from gnmi.models.target import Target
from gnmi.proto import target_pb2 as pb


def test_configuration_encode_empty():
    c = Configuration()
    encoded = c.encode()
    assert isinstance(encoded, pb.Configuration)
    assert len(encoded.request) == 0
    assert len(encoded.target) == 0


def test_configuration_round_trip_with_target():
    t = Target(hostaddr="r1.lab", port=6030)
    c = Configuration(target={"r1": t}, instance_id="inst-1", meta={"env": "lab"})
    encoded = c.encode()
    decoded = Configuration.decode(encoded)
    assert decoded.instance_id == "inst-1"
    assert decoded.meta == {"env": "lab"}
    assert "r1" in decoded.target
    assert decoded.target["r1"].hostaddr == "r1.lab"
    assert decoded.target["r1"].port == 6030


def test_configuration_instance_id_round_trip():
    c = Configuration(instance_id="test-123")
    decoded = Configuration.decode(c.encode())
    assert decoded.instance_id == "test-123"


def test_configuration_meta_round_trip():
    c = Configuration(meta={"k1": "v1", "k2": "v2"})
    decoded = Configuration.decode(c.encode())
    assert decoded.meta == {"k1": "v1", "k2": "v2"}
