# -*- coding: utf-8 -*-

"""Coverage for the async API-level wrapper functions in gnmi.api (T2)."""

from gnmi.api import acapabilities, aget, adelete, areplace, aupdate, asubscribe
from tests.conftest import STUB_GNMI_VERSION


async def test_acapabilities(stub_server):
    resp = await acapabilities(stub_server.target, insecure=True)
    assert resp.gnmi_version == STUB_GNMI_VERSION


async def test_aget(stub_server):
    notifs = []
    async for notif in aget(
        stub_server.target, ["/system/config/hostname"], insecure=True
    ):
        notifs.append(notif)
    assert len(notifs) >= 1
    assert str(notifs[0].updates[0].path) == "/system/config/hostname"


async def test_adelete(stub_server):
    resp = await adelete(stub_server.target, ["/a/b"], insecure=True)
    assert any(r.op.name == "DELETE" for r in resp.responses)


async def test_areplace(stub_server):
    resp = await areplace(stub_server.target, [("/c/d", "val")], insecure=True)
    assert any(r.op.name == "REPLACE" for r in resp.responses)


async def test_aupdate(stub_server):
    resp = await aupdate(stub_server.target, [("/e/f", "val")], insecure=True)
    assert any(r.op.name == "UPDATE" for r in resp.responses)


async def test_asubscribe(stub_server):
    notifs = []
    async for notif in asubscribe(
        stub_server.target,
        ["/system/config/hostname"],
        insecure=True,
        mode="once",
    ):
        notifs.append(notif)
    assert len(notifs) >= 1
