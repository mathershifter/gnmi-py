# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
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
import json
import os
import pathlib
import typing as t
from importlib.metadata import version

import click
import click_config_file
import grpc
import toml
from grpc import __version__ as grpc_version

from gnmi import util
from gnmi.async_session import AsyncSession
from gnmi.models import Subscription
from gnmi.models.notification import Notification
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


def _build_tls_config(
    ca: str, cert: str, key: str, get_target_certs: bool
) -> TLSConfig | None:
    if not (ca or cert or key or get_target_certs):
        return None
    return TLSConfig(
        ca_cert=open(ca, "rb").read() if ca else None,
        client_cert=open(cert, "rb").read() if cert else None,
        client_key=open(key, "rb").read() if key else None,
        get_server_cert=get_target_certs,
    )


def _new_session(ctx: click.Context) -> AsyncSession:
    """Build an AsyncSession from the click group's parsed options."""
    o = ctx.obj
    metadata: dict[str, str] = {}
    if o["username"]:
        metadata = {"username": o["username"], "password": o["password"] or ""}

    tls = _build_tls_config(
        o["tls_ca"], o["tls_cert"], o["tls_key"], o["tls_get_target_certificates"]
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


# ---------------------------------------------------------------------------
# Output helper (used by get / subscribe)
# ---------------------------------------------------------------------------

def write_notification(n: Notification, pretty: bool = False) -> None:
    notif: dict[str, t.Any] = {}

    updates = []
    for u in n.updates:
        val = u.value
        if val:
            if isinstance(val.value, bytes):
                val = val.value.decode("utf-8")
            else:
                val = str(val.value)
        updates.append({"path": str(u.path), "value": val})

    deletes = [{"path": str(d)} for d in n.deletes]

    if n.atomic:
        notif["atomic"] = True

    prefix = str(n.prefix)
    if prefix:
        notif["prefix"] = prefix
    if n.timestamp:
        notif["timestamp"] = n.timestamp
    if updates:
        notif["updates"] = updates
    if deletes:
        notif["deletes"] = deletes

    if pretty:
        click.echo(json.dumps(notif, separators=(", ", ": "), indent=2))
    else:
        click.echo(json.dumps(notif))


# ---------------------------------------------------------------------------
# Click command group + subcommands
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(format_version(), prog_name="gnmip")
@click.argument("target")
@click.option("--pretty", is_flag=True, default=False, help="pretty-print notifications")
@click.option("--tls-ca", default="", type=click.Path(), help="certificate authority")
@click.option("--tls-cert", default="", type=click.Path(), help="client certificate")
@click.option("--tls-key", default="", type=click.Path(), help="client key")
@click.option(
    "--tls-get-target-certificates",
    is_flag=True,
    default=False,
    help="fetch and validate the target's TLS cert before opening the gRPC channel",
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
    ctx.ensure_object(dict).update(kwargs)


@cli.command()
@click.pass_context
def capabilities(ctx: click.Context) -> None:
    """Discover supported models and encodings."""
    async def _run():
        async with _new_session(ctx) as sess:
            cap = await sess.capabilities()
            click.echo(f"gNMI Version: {cap.gnmi_version}")
            click.echo(
                "Encodings: "
                + ", ".join(e.name for e in cap.supported_encodings)
            )
            click.echo("Models:")
            for m in cap.supported_models:
                click.echo(f" {m.name}")
                click.echo(f"    Version:      {m.version or 'n/a'}")
                click.echo(f"    Organization: {m.organization}")
    asyncio.run(_run())


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
    "--get-type",
    "get_type",
    type=click.Choice(["all", "config", "state", "operational"]),
    default="all",
    show_default=True,
)
@click.pass_context
def get(ctx: click.Context, paths, encoding, prefix, get_type) -> None:
    """Fetch a snapshot for one or more paths."""
    async def _run():
        async with _new_session(ctx) as sess:
            rsp = await sess.get(
                paths=list(paths),
                prefix=prefix or None,
                encoding=encoding,
                data_type=get_type,
            )
            for notif in rsp.notifications:
                write_notification(notif, ctx.obj["pretty"])
    asyncio.run(_run())


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
@click.option("--interval", default="10s", show_default=True, help="sample interval (e.g. 10s, 500ms)")
@click.option("--heartbeat", default="", help="heartbeat interval (e.g. 30s)")
@click.option("--aggregate", is_flag=True, default=False, help="allow aggregation")
@click.option("--suppress", is_flag=True, default=False, help="suppress redundant updates")
@click.option("--qos", type=int, default=0, show_default=True, help="DSCP marking")
@click.pass_context
def subscribe(
    ctx: click.Context,
    paths,
    encoding,
    prefix,
    mode,
    submode,
    interval,
    heartbeat,
    aggregate,
    suppress,
    qos,
) -> None:
    """Subscribe to updates for one or more paths."""

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

    async def _run():
        async with _new_session(ctx) as sess:
            try:
                async for resp in sess.subscribe(
                    subscriptions=subs,
                    prefix=prefix or None,
                    encoding=encoding,
                    mode=mode,
                    qos=qos,
                    aggregate=aggregate,
                ):
                    if resp.sync_response:
                        if mode == "once":
                            break
                        continue
                    write_notification(resp.update, ctx.obj["pretty"])
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    return
                raise

    asyncio.run(_run())
