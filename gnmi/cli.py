# -*- coding: utf-8 -*-

"""
gnmi.cli — click-based CLI entry point for `gnmip`.

The command group exposes:

    gnmip [GLOBAL OPTIONS] TARGET capabilities
    gnmip [GLOBAL OPTIONS] TARGET get [PATHS...]
    gnmip [GLOBAL OPTIONS] TARGET subscribe [PATHS...]

Defaults can be loaded from a TOML config file (default ``~/.gnmirc``,
overridable with ``--config``). Top-level keys feed group options;
sections like ``[subscribe]`` feed the matching subcommand.
"""

import asyncio
import os
import pathlib
from importlib.metadata import version
from functools import wraps
import click
import click_config_file
import grpc
import toml
from grpc import __version__ as grpc_version

from gnmi import util
from gnmi.async_session import AsyncSession
from gnmi.models import Subscription
from gnmi.models.path import Path
from gnmi.models.target import target_factory
from gnmi.formatters.pretty import PrettyCapabilities, PrettyNotification
from gnmi.formatters.streams import StreamingNotification
from gnmi.formatters.json import JsonNotification, JsonCapabilities
from gnmi.tls import TLSConfig


GNMIRC_PATH = os.environ.get("GNMIRC_PATH", pathlib.Path.home())
# Always TOML. Distinct from --config FILE (which overrides rc defaults).
GNMIRC_FILENAMES = (".gnmirc", "_gnmirc")
# ---------------------------------------------------------------------------
# Version string and shared option groups
# ---------------------------------------------------------------------------


def format_version() -> str:
    return "gnmip %s [protobuf %s, grpcio %s]" % (
        version("gnmi"),
        grpc_version,
        version("protobuf"),
    )


def _toml_provider(file_path: str, _cmd_name: str) -> dict:
    """click-config-file provider that reads TOML."""
    with open(file_path, "r") as fh:
        return toml.load(fh)


def _yaml_provider(file_path: str, _cmd_name: str) -> dict:
    """click-config-file provider that reads YAML."""
    import yaml  # type: ignore[import]

    with open(file_path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _config_provider(file_path: str, cmd_name: str) -> dict:
    """Dispatch the --config FILE by extension. Defaults to TOML."""
    if file_path.endswith((".yaml", ".yml")):
        return _yaml_provider(file_path, cmd_name)
    return _toml_provider(file_path, cmd_name)


# ---------------------------------------------------------------------------
# load_rc — provides alternate defaults, auto-loaded from ~/.gnmirc
# ---------------------------------------------------------------------------
def load_rc() -> dict:
    """Return the rc-file contents as a click ``default_map`` dict.

    Searches ``~/.gnmirc`` then ``~/_gnmirc``. Returns an empty dict when
    no rc file exists. The rc layer feeds *defaults*; the ``--config``
    option (YAML or TOML) overrides them; explicit command-line flags
    override both.
    """
    home = pathlib.Path(GNMIRC_PATH)
    for name in GNMIRC_FILENAMES:
        path = home / name
        if path.exists():
            with open(path, "r") as fh:
                return toml.load(fh) or {}
    return {}


# ---------------------------------------------------------------------------
# Common option helpers
# ---------------------------------------------------------------------------

ENCODINGS = ["json", "bytes", "proto", "ascii", "json-ietf"]

FORMATTERS = ["pretty", "json", "jsonl", "yaml"]


def _build_tls_config(
    ca: str, cert: str, key: str, get_target_certs: bool, no_verify: bool
) -> TLSConfig | None:
    if not (ca or cert or key or get_target_certs):
        return None
    return TLSConfig(
        ca_cert=open(ca, "rb").read() if ca else None,
        client_cert=open(cert, "rb").read() if cert else None,
        client_key=open(key, "rb").read() if key else None,
        get_server_cert=get_target_certs,
        no_verify=no_verify,
    )


def _new_session(ctx: click.Context) -> AsyncSession:
    """Build an AsyncSession from the click group's parsed options."""
    o = ctx.obj
    metadata: dict[str, str] = {}
    if o["username"]:
        metadata = {"username": o["username"], "password": o["password"] or ""}

    tls = _build_tls_config(
        o["tls_ca"],
        o["tls_cert"],
        o["tls_key"],
        o["tls_get_target_certificate"],
        o["tls_no_verify"],
    )

    grpc_options: dict = {}
    if o["host_override"]:
        grpc_options["server_host_override"] = o["host_override"]

    return AsyncSession(
        o["target"],
        metadata=metadata,
        insecure=o["insecure"],
        tls=tls,
        grpc_options=grpc_options,
    )


def _build_prefix(prefix: str, target: str, without_target: bool) -> Path | None:
    """Build a prefix Path, optionally injecting the session host as ``Path.target``."""
    if not prefix and without_target:
        return None
    p = Path.from_str(prefix) if prefix else Path(elem=[])
    if not without_target:
        p.target = target_factory(target).hostaddr
    return p


def async_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(f(*args, **kwargs))
        except asyncio.CancelledError:
            print("Task was aborted/canceled.")
        except KeyboardInterrupt:
            print("\nInterrupted.")

    return wrapper


# ---------------------------------------------------------------------------
# Click command group + subcommands
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(format_version(), prog_name="gnmip")
@click.option(
    "--target",
    "-t",
    default="",
    help="gNMI target address (host:port). Can also be set via the config file.",
)
@click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    help="output notifications as JSON, short for --format json",
)
@click.option(
    "--format",
    default="pretty",
    type=click.Choice(FORMATTERS),
    help="output format (json, yaml, etc.)",
)
@click.option("--tls-ca", default="", type=click.Path(), help="certificate authority")
@click.option("--tls-cert", default="", type=click.Path(), help="client certificate")
@click.option("--tls-key", default="", type=click.Path(), help="client key")
@click.option(
    "--tls-get-target-certificate",
    is_flag=True,
    default=False,
    help="fetch and validate the target's TLS cert before opening the gRPC channel",
)
@click.option(
    "--tls-no-verify",
    is_flag=True,
    default=False,
    help="disable TLS certificate verification",
)
@click.option("--insecure", is_flag=True, default=False, help="disable TLS")
@click.option("--host-override", default="", help="override gRPC server hostname (SNI)")
@click.option("--debug-grpc", is_flag=True, default=False, help="enable gRPC debugging")
@click.option("-u", "--username", default="", help="username metadata")
@click.option("-p", "--password", default="", help="password metadata")
@click_config_file.configuration_option(
    cmd_name="gnmip",
    provider=_config_provider,
    implicit=False,
    help="Path to a YAML or TOML config file. Overrides ~/.gnmirc defaults.",
)
@click.pass_context
def cli(ctx: click.Context, **kwargs) -> None:
    """gNMI client."""
    if kwargs["debug_grpc"]:
        util.enable_grpc_debuging()

    # The --json flag is a shorthand for --format json, for convenience and backwards compatibility.
    if kwargs["json"]:
        kwargs["format"] = "json"
        del kwargs["json"]

    ctx.ensure_object(dict).update(kwargs)


@cli.command()
@click.pass_context
@async_command
async def capabilities(ctx: click.Context) -> None:
    """Discover supported models and encodings."""
    fmt = ctx.obj["format"]

    async with _new_session(ctx) as sess:
        cap = await sess.capabilities()
        if fmt == "pretty":
            PrettyCapabilities().send(cap)
        else:
            JsonCapabilities().send(cap)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option(
    "--encoding",
    type=click.Choice(ENCODINGS),
    default="json",
    show_default=True,
)
@click.option("--prefix", default="", help="path prefix")
@click.option(
    "--no-prefix-target",
    is_flag=True,
    default=False,
    help="set the prefix path's target field to the session host",
)
@click.option(
    "--get-type",
    "get_type",
    type=click.Choice(["all", "config", "state", "operational"]),
    default="all",
    show_default=True,
)
@click.pass_context
@async_command
async def get(
    ctx: click.Context, paths, encoding, prefix, no_prefix_target, get_type
) -> None:
    """Fetch a snapshot for one or more paths."""
    prefix_path = _build_prefix(
        prefix,
        ctx.obj["target"],
        no_prefix_target,
    )
    fmt = ctx.obj["format"]

    async with _new_session(ctx) as sess:
        rsp = await sess.get(
            paths=[p for p in paths],
            prefix=prefix_path,
            encoding=encoding,
            data_type=get_type,
        )
        for notif in rsp.notifications:
            if fmt == "pretty":
                PrettyNotification().send(notif)
            else:
                JsonNotification().send(notif)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option(
    "--encoding",
    type=click.Choice(ENCODINGS),
    default="json",
    show_default=True,
)
@click.option("--prefix", default="", help="path prefix")
@click.option(
    "--no-prefix-target",
    is_flag=True,
    default=False,
    help="set the prefix path's target field to the session host",
)
@click.option(
    "--mode",
    type=click.Choice(["stream", "once", "poll"]),
    default="stream",
    show_default=True,
)
@click.option(
    "--submode",
    type=click.Choice(["target-defined", "on-change", "sample"]),
    default="target-defined",
    show_default=True,
)
@click.option(
    "--interval",
    default="10s",
    show_default=True,
    help="sample interval (e.g. 10s, 500ms)",
)
@click.option("--heartbeat", default="", help="heartbeat interval (e.g. 30s)")
@click.option("--aggregate", is_flag=True, default=False, help="allow aggregation")
@click.option(
    "--suppress", is_flag=True, default=False, help="suppress redundant updates"
)
@click.option("--qos", type=int, default=0, show_default=True, help="DSCP marking")
@click.option(
    "--detail",
    is_flag=True,
    default=False,
    help="display detailed notification messages",
)
@click.pass_context
@async_command
async def subscribe(
    ctx: click.Context,
    paths,
    encoding,
    prefix,
    no_prefix_target,
    mode,
    submode,
    interval,
    heartbeat,
    aggregate,
    suppress,
    qos,
    detail,
) -> None:
    """Subscribe to updates for one or more paths."""

    prefix_path = _build_prefix(prefix, ctx.obj["target"], no_prefix_target)
    format = ctx.obj["format"]

    def _ns(d: str) -> int:
        return util.parse_duration(d) if d else 0

    subs = [
        Subscription(
            path=p,
            mode=submode,
            sample_interval=_ns(interval),
            heartbeat_interval=_ns(heartbeat),
            suppress_redundant=suppress,
        )
        for p in paths
    ]

    async with _new_session(ctx) as sess:
        try:
            async for resp in sess.subscribe(
                subscriptions=subs,
                prefix=prefix_path,
                encoding=encoding,
                mode=mode,
                qos=qos,
                aggregate=aggregate,
            ):
                if resp.sync_response:
                    if mode == "once":
                        break
                    continue
                # PrettyNotification().send(resp.update)

                if format == "pretty":
                    if detail:
                        PrettyNotification().send(resp.update)
                    else:
                        StreamingNotification().send(resp.update)
                else:
                    JsonNotification().send(resp.update)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                return
            raise


@cli.command()
@click.pass_context
@async_command
async def collector(ctx: click.Context) -> None:
    """Start a gNMI collector that listens for incoming notifications."""
    pass
