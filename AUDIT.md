# gnmi-py Code Audit

Scope: hand-written modules under `gnmi/` and `tests/`. Generated protobuf
code in `gnmi/proto/` is excluded.

## Bugs

### Critical

1. **Public API typo `capabilites` — `gnmi/__init__.py:16`, `gnmi/api.py:14,43`.**
   The function exported in `__all__` is misspelled. CLI and README use the
   correct `capabilities`, so user code copy-pasted from docs won't import.

2. **`--tls-cert` flag always crashes — `gnmi/cli.py:171`.** Reads
   `args.tls_get_server_certificates`, but argparse declares
   `--tls-get-target-certificates` (`cli.py:52`) →
   `tls_get_target_certificates`. Every TLS CLI invocation raises
   `AttributeError`. No test covers this branch.

<!-- 3. (rescinded) `get_server_cert=True` opens a TLS handshake to the
     target using the user-provided CA context and calls
     `ssl.getpeercert()` — it's an early validation step, not a cert
     *retrieval*. The discarded return is a parsed dict and would not be a
     drop-in `root_cert` (which needs PEM bytes). Two minor concerns
     remain: the flag name `--tls-get-target-certificates` is misleading,
     and if validation passes there's no observable effect. -->


4. **`GetRequest.encode` sends a `str` where proto wants an enum int —
   `gnmi/models/get.py:102`.** `type=self.type.name` passes `"ALL"` to a
   `DataType` enum field; protobuf rejects this. Same pattern in
   `UpdateResult.encode` (`update_result.py:69`).

5. **`DataType` factory passes `int` type object instead of value —
   `gnmi/models/get.py:90`.** `return DataType(int)` should be
   `DataType(typ)`. Always raises when an int is supplied.

6. **`SubscribeRequest.decode` is a no-op — `gnmi/models/subscribe.py:54-62`.**
   Hard-codes `sub=None, poll=None`; ignores `v.subscribe` and `v.poll`.
   Round-trip silently loses everything.

7. **`subscribe()` swallows `GrpcDeadlineExceeded` — `gnmi/api.py:220-221`.**
   `except GrpcDeadlineExceeded: pass` terminates the generator silently —
   caller can't distinguish "stream ended cleanly" from "timeout."

8. **`oneof(...)` rejects valid `False` — `gnmi/util.py:86`**, used in
   `SubscribeResponse.encode` (`subscribe.py:77`). `sync_response` is a proto
   bool; legitimate `False` is treated as "not set," default `False` is
   treated as set. Either way wrong.

### Important

9. **`Value.encode` mis-handles `LEAFLIST_VAL` —
   `gnmi/models/value.py:155-159`.** Iterates raw Python values (ints/strs)
   and calls `.encode()` on each; `int` has no `.encode`. Must wrap each in
   `Value(...).encode()` first.

10. **`Value.encode` double-encodes bytes for `ANY_VAL` — `value.py:151`.**
    `str(self.val).encode()` on already-bytes input yields `b"b'x'"`.

11. **Channel leak — `gnmi/session.py:82`.** `Session` opens a `grpc.Channel`
    but provides no `close()`, `__enter__`/`__exit__`, or `__del__`. Every
    high-level API call creates a Session and leaks a channel.

12. **`parse_duration` returns 0 for `"0s"` and bare numbers; can't parse
    compound durations — `gnmi/util.py:58`.** Guard `len(buf) > 0 and val > 0`
    drops zero values silently; no support for `"1m30s"`.

13. **`update_list_factory` silently drops non-list inputs —
    `gnmi/models/update.py:58-62`.** Declared type is `Sequence[UpdateItem_]`,
    but tuples/generators get an empty list with no error.

14. **`Subscriptions` descriptor silently drops unsupported items —
    `subscription_list.py:43-52`.** A `Path` in the input (which
    `Session.subscribe`'s signature claims to accept) is silently filtered
    out. Also uses class-level mutable `_default = []`.

15. **`entry.py:15` installs a SIGINT handler at import time.** Anyone
    importing `gnmi.entry` (e.g. tests) clobbers the process's SIGINT
    handler.

17. **`entry.py:12-16` calls `sys.exit(1)` at import time** when
    `pydantic` is missing. Importing `gnmi.entry` as a library (or from
    any tool that walks the package) terminates the entire process. The
    pydantic guard belongs inside `main()`, alongside the SIGINT install
    from #15 — module import must be side-effect-free.

<!-- 16. (rescinded) The "not idempotent on backslash" complaint assumed
     someone would feed already-escaped output back into escape_string.
     Real callers (`PathElem.__str__`) escape the raw field each time, and
     the path parser (`split_path` / `parse_elem`) unescapes `\\` → `\`,
     so the genuine round-trip `name → __str__ → from_str → name` is
     correct. A regression guard exercising that round-trip lives in
     tests/test_audit_bugs.py. -->


### Nit

- `gnmi/__init__.py:8` `version("gnmi")` raises `PackageNotFoundError` when
  run from an uninstalled checkout.
- `constantize` is misspelled in `gnmi/util.py:15` and called from many
  places.
- `gnmi/api.py:99` docstring typo `respones`.

## Documentation

<!-- All items in this section are addressed:
     - README rewritten for uv tooling, Session context-manager usage,
       TLS, ~/.gnmirc, and the full API surface.
     - `capabilities` typo fixed (bug #1 in Bugs/Critical).
     - Session.get / Session.subscribe docstrings updated to show keyword
       args instead of the non-existent `options=` dict.
     - All `gnmi.structures.CertificateStore` / `gnmi.messages.*`
       references replaced with the real types
       (`gnmi.session.TLSConfig`, `gnmi.models.*.<...>Response`).
     - BasicAuth and TLSConfig now exported from `gnmi.__all__` and
       documented in the README.
     - replace() / update() docstring examples no longer copy-pasted.
     - Class docstrings added to Subscription, SubscriptionList,
       Notification, Update, Value, Path.
     - Session.capabilities docstring shows the actual decoded type
       (list of Encoding enums). -->

## Testing

### Critical

1. **The entire network API is skipped without a live target.**
   `tests/test_api.py:13` and `tests/test_session.py:13` apply
   `pytest.mark.skipif(not GNMI_TARGET)` at module level. In CI without
   `GNMI_TARGET` set, `Session.get/set/subscribe/capabilities` and the
   high-level `api.get/set/...` wrappers run zero assertions. Fix: spin up
   an in-process `gNMIServicer` stub.

2. **`gnmi/cli.py` has only a happy-path `test_arg_loader`.** No coverage
   for `--tls-cert` (the always-crashing branch), `write_notification`,
   `load_rc`, `load_conf`, or `format_version`.

3. **`gnmi/certs.py:get_server_certificate` has zero tests.** Failure modes
   (closed socket, IPv6, `unix://`) untested.

### Important

4. **Decode round-trips are not tested for most models.**
   `SubscribeRequest.decode`, `SetResponse.decode`, `GetResponse.decode` are
   unexercised — Bug #6 (lossy subscribe decode) would have been caught by
   a single round-trip test.

5. **`parse_duration` tests only cover single-unit positive cases** — miss
   `"0s"`, bare numerics, compound, unknown unit.

6. **No tests exercise error paths** in any decoder, in `oneof` (zero /
   multiple set), or in the `RpcError` → `GrpcError` translation inside
   `Session`.

7. **`Path.from_str` edge cases** (`""`, `"/"`, trailing escape, origin
   containing `:` after content) untested.

8. **`gnmi/deserialize.py` only has a trivial test** — optional unwrapping,
   nested dataclasses, `list[dataclass]`, custom `deserialize_<name>`
   hooks, `omit_none=False` are all untested.

9. **No tests exercise the TLS branch in `Session._new_channel`**, which
   is why both the channel leak (Bug #11) and dead cert-fetch (Bug #3)
   shipped unnoticed.

10. **`tests/test_models_subscribe.py` is effectively empty** (header
    only); `tests/test_session.py:44`-ish contains
    `for resp.update in resp.update.updates` which is almost certainly a
    typo and not what was intended.

### Nit

- `test_models_capabilities.py` is large but only smoke-tests one decode
  fixture; no encode round-trip, no empty-models case.
- `test_util.test_escape_string` only one input — backslash round-trip
  (Bug #16) untested.

---

**Highest-leverage fixes:** typo in `capabilites`; CLI TLS arg crash
(`cli.py:171`); `GetRequest`/`UpdateResult` enum-as-string; lossy
`SubscribeRequest.decode`; channel leak; `oneof` on bool fields;
in-process gRPC stub to actually exercise `Session`; round-trip tests for
every model.
