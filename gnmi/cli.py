# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import argparse
import json
import pathlib
import typing as t

from collections.abc import Sequence
from importlib.metadata import version

from grpc import __version__ as grpc_version

from gnmi import config
from gnmi.environments import GNMIRC_PATH
from gnmi.constants import GNMIRC_FILES
from gnmi.models import Notification

def format_version():

    elems = (version("gnmi"), grpc_version, version("protobuf"))

    return "gnmip %s [protobuf %s, grpcio %s]" % elems

def parse_args(args: t.Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=format_version())
    parser.add_argument("target", help="gNMI gRPC server")
    parser.add_argument(
        "operation",
        type=str,
        choices=["capabilities", "get", "subscribe"],
        help="gNMI operation [capabilities, get, subscribe]",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="pretty print notifications",
    )
    # parser.add_argument(
    #     "-c", "--config", type=str, default=None, help="Path to gNMI config file"
    # )

    # parser.add_argument("--use-alias", action="store_true", help="use server name alias")

    parser.add_argument("--tls-ca", default="", type=str, help="certificate authority")
    parser.add_argument("--tls-cert", default="", type=str, help="client certificate")
    parser.add_argument("--tls-key", default="", type=str, help="client key")
    parser.add_argument("--tls-get-target-certificates", action="store_true", default=False, help="retrieve certificates from the target")
    parser.add_argument("--insecure", action="store_true", help="disable TLS")
    parser.add_argument(
        "--host-override", default=None, help="Override gRPC server hostname"
    )

    grpc_ = parser.add_argument_group("gRPC options")
    grpc_.add_argument(
        "--debug-grpc", action="store_true", help="enable gRPC debugging"
    )

    md = parser.add_argument_group("metadata")
    md.add_argument("-u", "--username", default="")
    md.add_argument("-p", "--password", default="")

    common = parser.add_argument_group("Common options")
    common.add_argument(
        "--encoding",
        default="json",
        type=str,
        choices=["json", "bytes", "proto", "ascii", "json-ietf"],
        help="set encoding",
    )
    common.add_argument(
        "--prefix", default="", type=str, help="gRPC path prefix (default: <empty>)"
    )

    get = parser.add_argument_group("Get options")
    get.add_argument(
        "--get-type", type=str, default="all", choices=["all", "config", "state", "operational"]
    )
    get.add_argument("paths", nargs="*", default=[])

    #parser.add_argument_group("Replace options")

    sub = parser.add_argument_group("Subscribe options")
    sub.add_argument(
        "--interval",
        default=None,
        type=str,
        help="sample interval in milliseconds (default: 10s)",
    )

    # sub.add_argument(
    #     "--timeout",
    #     default=None,
    #     type=int,
    #     help="operation timeout in seconds (default: None)",
    # )

    sub.add_argument(
        "--heartbeat",
        default=None,
        type=str,
        help="heartbeat interval in milliseconds (default: None)",
    )
    sub.add_argument("--aggregate", action="store_true", help="allow aggregation")
    sub.add_argument("--suppress", action="store_true", help="suppress redundant")
    sub.add_argument(
        "--mode",
        default=None,
        type=str,
        choices=["stream", "once", "poll"],
        help="Specify subscription mode",
    )
    sub.add_argument(
        "--submode",
        default=None,
        type=str,
        choices=["target-defined", "on-change", "sample"],
        help="subscription sub-mode",
    )
    # sub.add_argument(
    #     "--once",
    #     action="store_true",
    #     default=False,
    #     help=(
    #         "End subscription after first sync_response. This is a "
    #         "workaround for implementations that do not support 'once' "
    #         "subscription mode"
    #     ),
    # )
    sub.add_argument(
        "--qos",
        default=0,
        type=int,
        help="DSCP value to be set on transmitted telemetry",
    )

    # group.add_argument("--tls-no-verify", action="store_true", help="")

    parsed = parser.parse_args(args)

    return parsed

def arg_loader(args: argparse.Namespace) -> dict[str, t.Any]:


    loaded = {
        # gnmi_version=
        "target": args.target,
        "insecure": args.insecure,
        # "tls": args.tls,
        "debug_grpc": args.debug_grpc,
        "pretty": args.pretty,
        # "metadata": args.metadata
    }

    if args.username:
        loaded["metadata"] = {
            "username": args.username,
            "password": args.password,
        }

    if args.tls_cert:
        loaded["tls"] = {
            "ca_cert": args.tls_ca,
            "cert": args.tls_cert,
            "key": args.tls_key,
            "get_server_certificates": args.tls_get_server_certificates
        }

    if  args.operation == "capabilities":
        loaded["capabilities"] = {}
    elif args.operation == "get":
        loaded["get"] = {
            "prefix": args.prefix,
            "paths": args.paths,
            "encoding": args.encoding,
            "type": args.get_type,
        }
    elif args.operation == "subscribe":
        subs = []
        for p in args.paths:
            subs.append({
                "path": p,
                "mode": args.submode,
                "suppress_redundant": args.suppress,
                "sample_interval": args.interval,
                "heartbeat_interval": args.heartbeat
            })
        loaded["subscribe"] = {
            "subscriptions": subs,
            "prefix": args.prefix,
            "qos": args.qos,
            "mode": args.mode,
            "encoding": args.encoding,
        }

    return loaded

def load_conf() -> config.Config:
    return config.load(arg_loader, parse_args())

def load_rc() -> t.Any:
    path = pathlib.Path(GNMIRC_PATH)
    for f in GNMIRC_FILES:
        path = path / f
        if path.exists():
            with path.open("r") as fh:
                return config.load(config.yaml_loader, fh.read())
    return config.Config()

def write_notification(n: Notification, pretty: bool = False) -> None:
    notif: dict[str, t.Any] = {}

    updates = []
    for u in n.updates:
        val = u.value

        if isinstance(val.value, bytes):
            val = val.value.decode("utf-8")
        else:
            val = str(val.value)

        updates.append({"path": str(u.path), "value": val})

    deletes = []
    for d in n.deletes:
        deletes.append({"path": str(d)})

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

    # print(notif)
    if pretty:
        print(json.dumps(notif, separators=(", ", ": "), indent=2))
    else:
        print(json.dumps(notif))
