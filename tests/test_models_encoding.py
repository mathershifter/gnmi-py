
from gnmi.proto import gnmi_pb2 as pb

def test_encoding():
    from gnmi.models.encoding import Encoding
    
    assert Encoding.JSON.encode() == pb.Encoding.JSON   
    assert Encoding.decode(pb.Encoding.JSON) == Encoding.JSON