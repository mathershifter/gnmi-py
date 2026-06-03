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
import enum
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
from gnmi._env import env

# ---------------------------------------------------------------------------
# Version string and shared option groups
# ---------------------------------------------------------------------------


def format_version() -> str:
    return f"gnmip {version('gnmi')} [protobuf {version('protobuf')}, grpcio {grpc_version}]"


def _toml_provider(file_path: str, _cmd_name: str) -> dict:
    with open(file_path, "r") as fh:
        return toml.load(fh)


def _yaml_provider(file_path: str, _cmd_name: str) -> dict:
    import yaml  # type: ignore[import]

    with open(file_path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _config_provider(file_path: str, cmd_name: str) -> dict:
    if file_path.endswith((".yaml", ".yml")):
        return _yaml_provider(file_path, cmd_name)
    return _toml_provider(file_path, cmd_name)


# ---------------------------------------------------------------------------
# load_rc — provides alternate defaults, auto-loaded from ~/.gnmirc
# ---------------------------------------------------------------------------
def load_rc() -> dict:
    for p in env.GNMIP_RC_PATH:
        if p.is_file():
            return _config_provider(str(p), "gnmip")
    return {}


# ---------------------------------------------------------------------------
# Common option helpers
# ---------------------------------------------------------------------------


def _build_tls_config(
    ca: str, cert: str, key: str, get_target_certs: bool, no_verify: bool
) -> TLSConfig | None:
    ca_cert = client_cert = client_key = None

    if ca:
        with open(ca, "rb") as f:
            ca_cert = f.read()
    if cert:
        with open(cert, "rb") as f:
            client_cert = f.read()
    if key:
        with open(key, "rb") as f:
            client_key = f.read()

    return TLSConfig(
        ca_cert=ca_cert,
        client_cert=client_cert,
        client_key=client_key,
        get_server_cert=get_target_certs,
        no_verify=no_verify,
    )


def _new_session(ctx: click.Context, target: str) -> AsyncSession:
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
        target=target,
        metadata=metadata,
        insecure=o["insecure"],
        tls=tls,
        grpc_options=grpc_options,
    )


def _build_prefix(prefix: str, target: str, without_target: bool) -> Path | None:
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
        except asyncio.CancelledError as e:
            print(f"Task was aborted/canceled: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted.")

    return wrapper


class Encoding(enum.Enum):
    JSON = "json"
    BYTES = "bytes"
    PROTO = "proto"
    ASCII = "ascii"
    JSON_IETF = "json-ietf"

 
class Formatter(enum.Enum):
    PRETTY = "pretty"
    JSON = "json"
    JSONL = "jsonl"
    YAML = "yaml"


# ---------------------------------------------------------------------------
# Click command group + subcommands
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(format_version(), prog_name="gnmip")
@click.option(
    "--target",
    "-t",
    multiple=True,
    type=str,
    default=[env.GNMIP_TARGET],
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
    default=Formatter(env.GNMIP_FORMAT.lower()),
    type=click.Choice(Formatter, case_sensitive=False),
    help="output format (json, yaml, etc.)",
)
@click.option(
    "--rc-path",
    multiple=True,
    default=env.GNMIP_RC_PATH,
    help="Path to the gNMI config file",
)
@click.option(
    "--tls-ca",
    default=env.GNMIP_TLS_CA,
    type=click.Path(),
    help="certificate authority",
)
@click.option(
    "--tls-cert",
    default=env.GNMIP_TLS_CERT,
    type=click.Path(),
    help="client certificate",
)
@click.option(
    "--tls-key", default=env.GNMIP_TLS_KEY, type=click.Path(), help="client key"
)
@click.option(
    "--tls-get-target-certificate",
    is_flag=True,
    default=env.GNMIP_TLS_GET_TARGET_CERTIFICATE,
    help="fetch and validate the target's TLS cert before opening the gRPC channel",
)
@click.option(
    "--tls-no-verify",
    is_flag=True,
    default=env.GNMIP_TLS_NO_VERIFY,
    help="disable TLS certificate verification",
)
@click.option(
    "--insecure", is_flag=True, default=env.GNMIP_INSECURE, help="disable TLS"
)
@click.option(
    "--host-override",
    default=env.GNMIP_HOST_OVERRIDE,
    help="override gRPC server hostname (SNI)",
)
@click.option(
    "--debug-grpc",
    is_flag=True,
    default=env.GNMIP_DEBUG_GRPC,
    help="enable gRPC debugging",
)
@click.option("-u", "--username", default=env.GNMIP_USER, help="username metadata")
@click.option("-p", "--password", default=env.GNMIP_PASS, help="password metadata")
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
        kwargs["format"] = Formatter.JSON
        del kwargs["json"]

    ctx.ensure_object(dict).update(kwargs)


@cli.command()
@click.pass_context
@async_command
async def capabilities(ctx: click.Context) -> None:
    fmt = ctx.obj["format"]

    async def _run(target: str) -> None:
        async with _new_session(ctx, target) as sess:
            cap = await sess.capabilities()
            if fmt == Formatter.PRETTY:
                PrettyCapabilities().send(cap)
            else:
                JsonCapabilities().send(cap)

    tasks = []
    for target in ctx.obj["target"]:
        tasks.append(_run(target))
    await asyncio.gather(*tasks)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option(
    "--encoding",
    type=click.Choice(Encoding, case_sensitive=False),
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
    
    async def _run(target: str) -> None:
        prefix_path = _build_prefix(
            prefix,
            target,
            no_prefix_target,
        )
        fmt = ctx.obj["format"]
        async with _new_session(ctx, target) as sess:
            rsp = await sess.get(
                paths=[p for p in paths],
                prefix=prefix_path,
                encoding=encoding.value,
                data_type=get_type,
            )
            for notif in rsp.notifications:
                if fmt == Formatter.PRETTY:
                    PrettyNotification().send(notif)
                else:
                    JsonNotification().send(notif)

    tasks = []
    for target in ctx.obj["target"]:
        tasks.append(_run(target))

    await asyncio.gather(*tasks)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option(
    "--encoding",
    type=click.Choice(Encoding, case_sensitive=False),
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
    
    fmt = ctx.obj["format"]

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

    async def _run(target: str) -> None:
        prefix_path = _build_prefix(prefix, target, no_prefix_target)
        async with _new_session(ctx, target) as sess:
            try:
                async for resp in sess.subscribe(
                    subscriptions=subs,
                    prefix=prefix_path,
                    encoding=encoding.value,
                    mode=mode,
                    qos=qos,
                    aggregate=aggregate,
                ):
                    if resp.sync_response:
                        if mode == "once":
                            return
                        continue

                    if fmt == Formatter.PRETTY:
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
    
    tasks = []
    for target in ctx.obj["target"]:
        tasks.append(_run(target))
    
    await asyncio.gather(*tasks)

@cli.command()
@click.pass_context
@async_command
async def collector(ctx: click.Context) -> None:
    raise NotImplementedError("collector command is not implemented yet")
