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
gnmip [options] -t TARGET {capabilities|get|subscribe|collector} [paths ...]
```

Global flags (before the subcommand):

| flag | what it does |
|------|--------------|
| `-t TARGET` / `--target TARGET` | target host and port |
| `--insecure` | skip TLS (plaintext gRPC) |
| `--tls-ca PATH` | CA cert to validate the target |
| `--tls-cert PATH` / `--tls-key PATH` | client cert / key (mTLS) |
| `--tls-get-target-certificate` | early-validate the target cert before opening the gRPC channel |
| `--tls-no-verify` | disable TLS certificate verification |
| `--host-override HOST` | override the gRPC SNI / authority |
| `-u USER` / `-p PASS` | username / password metadata |
| `-j` / `--json` | shorthand for `--format json` |
| `--format {pretty,json,jsonl,yaml}` | output format (default: `pretty`) |
| `--rc-path PATH` | config file path(s) (default: `~/.gnmirc`) |
| `--config FILE` | explicit YAML or TOML config file |
| `--debug-grpc` | enable gRPC debug logging |

Get flags (after `get`):

| flag | default |
|------|---------|
| `--encoding {json,bytes,proto,ascii,json-ietf}` | `json` |
| `--prefix PATH` | unset |
| `--no-prefix-target` | off |
| `--get-type {all,config,state,operational}` | `all` |

Subscribe flags (after `subscribe`):

| flag | default |
|------|---------|
| `--encoding {json,bytes,proto,ascii,json-ietf}` | `json` |
| `--prefix PATH` | unset |
| `--no-prefix-target` | off |
| `--mode {stream,once,poll}` | `stream` |
| `--submode {target-defined,on-change,sample}` | `target-defined` |
| `--interval N` | `10s` (sample interval) |
| `--heartbeat N` | unset |
| `--aggregate` / `--suppress` / `--qos N` | off / off / 0 |
| `--detail` | off (show full notification objects) |

Examples:

```bash
gnmip --insecure -u admin -t localhost:6030 capabilities
gnmip --insecure -u admin -t localhost:6030 get /system/config/hostname
gnmip --insecure -u admin -t localhost:6030 subscribe /interfaces

# pipe to jq
gnmip --insecure -u admin -t localhost:6030 subscribe /system | \
  jq '{time: .time, path: (.prefix + .updates[].path), value: .updates[].value}'
```

### `~/.gnmirc`

`gnmip` reads `~/.gnmirc` if present. Override the config file path(s)
with `GNMIP_RC_PATH`. The file is **TOML** — top-level keys map to
global CLI flags and sections map to subcommand defaults. Example:

```toml
target = "r1.lab:6030"
insecure = true
username = "admin"
password = ""

[get]
encoding = "json"

[subscribe]
encoding = "json"
mode = "stream"
submode = "on-change"
```

`.toml` / `.yaml` / `.yml` files passed via `--config` are dispatched by
extension; `~/.gnmirc` is always parsed as TOML.

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

### Async API

Async equivalents of the top-level helpers are available in `gnmi.api`:

```python
from gnmi.api import acapabilities, aget, asubscribe, adelete, areplace, aupdate

async for notif in aget("localhost:6030", ["/system/config/hostname"],
                        insecure=True, auth=("admin", "")):
    for upd in notif.updates:
        print(upd.path, upd.value.value)
```

These are async generators (use `async for`, not `asyncio.run()`).

### Other exports

- **`gnmi.env`** — `Env` dataclass populated from `GNMIP_*` environment
  variables (target, auth, TLS, format defaults).
- **`gnmi.get_server_certificate(target, context, pem)`** — fetch a
  target's TLS certificate via a raw socket handshake.

## Exceptions

`gnmi-py` propagates the native gRPC exceptions without translation:

- **Sync**: `Session.*` raises `grpc.RpcError` on non-OK status.
- **Async**: `AsyncSession.*` raises `grpc.aio.AioRpcError`
  (a subclass of `grpc.RpcError`, so `except grpc.RpcError` catches
  both transports uniformly).

Use `e.code()` (`grpc.StatusCode.*`) to switch on the failure mode and
`e.details()` for the server-supplied message. `gnmi.exceptions` only
contains internal markers like `GnmiDeprecationError`.
