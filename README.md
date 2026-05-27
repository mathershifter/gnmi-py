# gnmi-py

A Python [gNMI](https://github.com/openconfig/gnmi) client. Ships with a
small Python API and a `gnmip` CLI.

Requires **Python 3.10 or newer**.

## Install

End users:

```bash
pip install git+https://github.com/mathershifter/gnmi-py.git
# or, for the CLI extras (click+rich):
pip install "gnmi[cli] @ git+https://github.com/mathershifter/gnmi-py.git"
```

Developers (this repo uses [`uv`](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/mathershifter/gnmi-py.git
cd gnmi-py
uv sync
uv run pytest
```

## CLI

```text
gnmip [target] [capabilities|get|subscribe] [paths ...]
```

Common flags:

| flag | what it does |
|------|--------------|
| `--insecure` | skip TLS (plaintext gRPC) |
| `--tls-ca PATH` | CA cert to validate the target |
| `--tls-cert PATH` / `--tls-key PATH` | client cert / key (mTLS) |
| `--tls-get-target-certificate` | early-validate the target cert before opening the gRPC channel |
| `--host-override HOST` | override the gRPC SNI / authority |
| `-u USER` / `-p PASS` | username / password metadata |
| `--encoding {json,bytes,proto,ascii,json-ietf}` | wire encoding |
| `--prefix PATH` | path prefix |

Subscribe-only:

| flag | default |
|------|---------|
| `--mode {stream,once,poll}` | `stream` |
| `--submode {target-defined,on-change,sample}` | `target-defined` |
| `--interval N` | `10s` (sample interval) |
| `--heartbeat N` | unset |
| `--aggregate` / `--suppress` / `--qos N` | off / off / 0 |

Examples:

```bash
gnmip --insecure -u admin localhost:6030 capabilities
gnmip --insecure -u admin localhost:6030 get /system/config/hostname
gnmip --insecure -u admin localhost:6030 subscribe /interfaces

# pipe to jq
gnmip --insecure -u admin localhost:6030 subscribe /system | \
  jq '{time: .time, path: (.prefix + .updates[].path), value: .updates[].value}'
```

### `~/.gnmirc`

`gnmip` reads `~/.gnmirc` (or `~/_gnmirc`) if present. Override the
search directory with `GNMIRC_PATH`. The file is **TOML** and matches
the shape of the `Config` model in `gnmi/config.py`. Example:

```toml
target = "r1.lab:6030"
insecure = true

[metadata]
username = "admin"
password = ""

[subscribe]
encoding = "json"
mode = "stream"

[[subscribe.subscriptions]]
path = "/interfaces"
mode = "on-change"
```

`.toml` / `.yaml` / `.yml` files passed elsewhere via the config loader
are dispatched by extension; the bare `.gnmirc` / `_gnmirc` names are
always parsed as TOML.

## Python API

Top-level helpers — each opens a short-lived `Session`, runs one RPC, and
closes the channel:

```python
from gnmi import capabilities, get, subscribe, update, replace, delete

resp = capabilities("localhost:6030", insecure=True, auth=("admin", ""))
print(resp.gnmi_version)

for notif in get("localhost:6030", ["/system/config/hostname"],
                 insecure=True, auth=("admin", "")):
    for upd in notif.updates:
        print(upd.path, upd.value.value)

for notif in subscribe("localhost:6030", ["/interfaces"],
                       insecure=True, auth=("admin", ""), mode="once"):
    for upd in notif.updates:
        print(upd.path, upd.value.value)

update("localhost:6030",
       updates=[("/system/config/hostname", "router1")],
       insecure=True, auth=("admin", ""))
```

For multiple RPCs against the same target, use `Session` directly as a
context manager so the channel is reused and cleanly closed:

```python
from gnmi import Session

with Session("localhost:6030", insecure=True,
             metadata={"username": "admin", "password": ""}) as sess:
    caps = sess.capabilities()
    resp = sess.get(["/system/config/hostname"])
    for notif in resp.notifications:
        for upd in notif.updates:
            print(upd.path, upd.value.value)
```

### TLS

```python
from gnmi import Session, TLSConfig

with open("ca.pem", "rb") as fh:
    ca = fh.read()
with open("client.pem", "rb") as fh:
    cert = fh.read()
with open("client.key", "rb") as fh:
    key = fh.read()

tls = TLSConfig(
    ca_cert=ca,
    client_cert=cert,
    client_key=key,
    # Optional: perform an early TLS handshake against the target so a bad
    # CA / hostname mismatch surfaces before any gNMI RPC is attempted.
    get_server_cert=False,
)

with Session("r1.lab:6030", tls=tls) as sess:
    print(sess.capabilities().gnmi_version)
```

### Subscribe — handling timeouts

`Session.subscribe` is a streaming iterator. Wrap it in a try/except for
deadline handling:

```python
import grpc
from gnmi import Session

with Session("r1.lab:6030", insecure=True) as sess:
    try:
        for resp in sess.subscribe(["/interfaces"], timeout=10):
            if resp.sync_response:
                break  # ONCE mode finished
            for upd in resp.update.updates:
                print(upd.path, upd.value.value)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
            raise
```

`AsyncSession.subscribe` works the same way — `async for` over the
iterator and catch `grpc.RpcError` (which `grpc.aio.AioRpcError`
subclasses).

## Exceptions

`gnmi-py` propagates the native gRPC exceptions without translation:

- **Sync**: `Session.*` raises `grpc.RpcError` on non-OK status.
- **Async**: `AsyncSession.*` raises `grpc.aio.AioRpcError`
  (a subclass of `grpc.RpcError`, so `except grpc.RpcError` catches
  both transports uniformly).

Use `e.code()` (`grpc.StatusCode.*`) to switch on the failure mode and
`e.details()` for the server-supplied message. `gnmi.exceptions` only
contains internal markers like `GnmiDeprecationError`.
