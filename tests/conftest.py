import os
from concurrent import futures

import asyncio
import pytest
import grpc

from gnmi.proto import gnmi_pb2 as pb
from gnmi.proto import gnmi_pb2_grpc
from gnmi.session import TLSConfig

GNMI_INSECURE: bool = True if os.environ.get("GNMI_INSECURE") else False
GNMI_TARGET: str = os.environ.get("GNMI_TARGET", "")
GNMI_USER: str = os.environ.get("GNMI_USER", "admin")
GNMI_PASS: str = os.environ.get("GNMI_PASS", "")
GNMI_ROOT_CERT: str = os.environ.get("GNMI_ROOT_CERT", "/dev/null")
GNMI_PRIVAE_KEY: str = os.environ.get("GNMI_PRIVAE_KEY", "/dev/null")
GNMI_CERT_CHAIN: str = os.environ.get("GNMI_CERT_CHAIN", "/dev/null")
GNMI_AUTH: tuple[str, str] = (GNMI_USER, GNMI_PASS)

# When no live gNMI device is provided, fall back to the in-process stub
# server below. Tests that fundamentally need a real device (state
# mutation, deadline-driven streaming) should gate on HAS_LIVE_TARGET.
HAS_LIVE_TARGET: bool = bool(GNMI_TARGET)

requires_live_target = pytest.mark.skipif(
    not HAS_LIVE_TARGET,
    reason="requires a live gNMI target (set GNMI_TARGET to enable)",
)


# ---------------------------------------------------------------------------
# In-process gNMI stub server (AUDIT.md Testing #1)
# ---------------------------------------------------------------------------
#
# Lets Session.* and api.* exercise real gRPC plumbing in CI, instead of
# silently skipping every assertion when GNMI_TARGET is unset. The stub is
# intentionally minimal: just enough behavior to round-trip the four RPCs
# and serve as the default backend for `target` / `tlsconfig` /
# `is_insecure` when no live target is configured. Tests can substitute
# their own handlers via ``stub_server.servicer.*``.

STUB_GNMI_VERSION = "0.10.0-stub"
STUB_HOSTNAME = "stub-target"

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

def _path_key(p: pb.Path) -> bytes:
    """Stable, hashable key for a proto Path."""
    return p.SerializeToString(deterministic=True)


class StubGNMIServicer(gnmi_pb2_grpc.gNMIServicer):
    """Programmable gNMI servicer.

    Each RPC handler is a swappable callable so tests can install bespoke
    behavior (errors, custom payloads, streams) without subclassing.

    The default Get/Set handlers maintain a tiny in-memory key/value store
    keyed by serialized Path, which is enough for the existing
    test_api.py / test_session.py round-trips to pass against the stub.
    """

    def __init__(self):
        self.last_capability_request = None
        self.last_get_request = None
        self.last_set_request = None
        self.last_subscribe_requests: list[pb.SubscribeRequest] = []
        self.last_metadata: list[tuple[str, str]] = []

        # Backing store for default get/set behavior.
        self.store: dict[bytes, pb.TypedValue] = {}

        self.capabilities_handler = self._default_capabilities
        self.get_handler = self._default_get
        self.set_handler = self._default_set
        self.subscribe_handler = self._default_subscribe

    # --- defaults -----------------------------------------------------

    def _default_capabilities(self, request, context):
        return pb.CapabilityResponse(
            gNMI_version=STUB_GNMI_VERSION,
            supported_encodings=[pb.JSON, pb.JSON_IETF],
            supported_models=[
                pb.ModelData(
                    name="openconfig-system",
                    organization="OpenConfig",
                    version="1.0.0",
                )
            ],
        )

    def _default_get(self, request, context):
        notifications = []
        for path in request.path:
            val = self.store.get(
                _path_key(path),
                pb.TypedValue(string_val=STUB_HOSTNAME),
            )
            notifications.append(
                pb.Notification(
                    timestamp=1,
                    prefix=request.prefix if request.HasField("prefix") else None,
                    update=[pb.Update(path=path, val=val)],
                )
            )
        return pb.GetResponse(notification=notifications)

    def _default_set(self, request, context):
        results = []
        for d in request.delete:
            self.store.pop(_path_key(d), None)
            results.append(pb.UpdateResult(path=d, op=pb.UpdateResult.DELETE))
        for r in request.replace:
            self.store[_path_key(r.path)] = r.val
            results.append(pb.UpdateResult(path=r.path, op=pb.UpdateResult.REPLACE))
        for u in request.update:
            self.store[_path_key(u.path)] = u.val
            results.append(pb.UpdateResult(path=u.path, op=pb.UpdateResult.UPDATE))
        return pb.SetResponse(
            prefix=request.prefix if request.HasField("prefix") else None,
            response=results,
            timestamp=1,
        )

    def _default_subscribe(self, request_iterator, context):
        # Echo each subscribed path as a single update, then send sync.
        for req in request_iterator:
            self.last_subscribe_requests.append(req)
            if not req.HasField("subscribe"):
                continue
            sl = req.subscribe
            for sub in sl.subscription:
                val = self.store.get(
                    _path_key(sub.path),
                    pb.TypedValue(string_val=STUB_HOSTNAME),
                )
                yield pb.SubscribeResponse(
                    update=pb.Notification(
                        timestamp=1,
                        prefix=sl.prefix if sl.HasField("prefix") else None,
                        update=[pb.Update(path=sub.path, val=val)],
                    )
                )
            yield pb.SubscribeResponse(sync_response=True)

    # --- dispatch -----------------------------------------------------

    def Capabilities(self, request, context):
        self.last_capability_request = request
        self.last_metadata = list(context.invocation_metadata())
        return self.capabilities_handler(request, context)

    def Get(self, request, context):
        self.last_get_request = request
        self.last_metadata = list(context.invocation_metadata())
        return self.get_handler(request, context)

    def Set(self, request, context):
        self.last_set_request = request
        self.last_metadata = list(context.invocation_metadata())
        return self.set_handler(request, context)

    def Subscribe(self, request_iterator, context):
        self.last_metadata = list(context.invocation_metadata())
        yield from self.subscribe_handler(request_iterator, context)


class _StubServer:
    def __init__(self, server: grpc.Server, servicer: StubGNMIServicer, port: int):
        self.server = server
        self.servicer = servicer
        self.port = port

    @property
    def target(self) -> str:
        return f"127.0.0.1:{self.port}"


@pytest.fixture
def stub_server():
    servicer = StubGNMIServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    gnmi_pb2_grpc.add_gNMIServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    try:
        yield _StubServer(server, servicer, port)
    finally:
        server.stop(grace=None)


@pytest.fixture
def stub_target(stub_server) -> str:
    return stub_server.target


# ---------------------------------------------------------------------------
# Backend-agnostic fixtures
# ---------------------------------------------------------------------------
# With GNMI_TARGET set: use the real device and the user's TLS material.
# Without: spin up the stub server and run insecure against it. Tests that
# need behaviors the stub can't reproduce should use @requires_live_target.

@pytest.fixture
def target(request) -> str:
    if HAS_LIVE_TARGET:
        return GNMI_TARGET
    return request.getfixturevalue("stub_server").target


@pytest.fixture
def tlsconfig() -> TLSConfig | None:
    if not HAS_LIVE_TARGET:
        return None
    with open(GNMI_ROOT_CERT, "r") as fh:
        root_cert = fh.read().encode()
    with open(GNMI_CERT_CHAIN) as fh:
        client_cert = fh.read().encode()
    with open(GNMI_PRIVAE_KEY) as fh:
        client_key = fh.read().encode()

    return TLSConfig(
        ca_cert=root_cert,
        client_cert=client_cert,
        client_key=client_key,
    )


@pytest.fixture
def is_insecure() -> bool:
    if not HAS_LIVE_TARGET:
        return True
    return GNMI_INSECURE
