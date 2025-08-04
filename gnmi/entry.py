# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import signal
import sys

from gnmi.session import Session, TLSConfig
from gnmi.models import Subscription
from gnmi.exceptions import GrpcDeadlineExceeded
from gnmi import cli, util

def signal_handler(*_, **__):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    cnf = cli.load_conf()

    if cnf.debug_grpc:
        util.enable_grpc_debuging()

    grpc_options: dict = {}
    tls_config = None
    if cnf.tls:
        tls_config = TLSConfig(
            ca_cert=cnf.tls.ca_cert,
            cert=cnf.tls.cert,
            key=cnf.tls.key,
            get_server_cert=cnf.tls.get_server_certificates
        )
    sess = Session(
        cnf.target,
        metadata=cnf.metadata,
        insecure=cnf.insecure,
        tls=tls_config,
        grpc_options=grpc_options,
    )

    if cnf.capabilities:
        cap_response = sess.capabilities()
        print(f"gNMI Version: {cap_response.gnmi_version}")
        print(
            f"Encodings: {', '.join([i.name for i in cap_response.supported_encodings])}"
        )
        print("Models:")
        for model in cap_response.supported_models:
            print(f" {model.name}")
            print(f"    Version:      {model.version or 'n/a'}")
            print(f"    Organization: {model.organization}")

    elif cnf.get:
        # options: GetOptions = cnf.get.options
        # paths = config.Get.paths
        rsp = sess.get(
            paths=cnf.get.paths,
            prefix=cnf.get.prefix,
            encoding=cnf.get.encoding,
            data_type=cnf.get.type
        )

        for notif in rsp.notifications:
            cli.write_notification(notif, cnf.pretty)

    elif cnf.subscribe:
        subs = []
        for sub in cnf.subscribe.subscriptions:
            subs.append(Subscription(
                path=sub.path,
                mode=sub.mode,
                sample_interval=sub.sample_interval,
                heartbeat_interval=sub.heartbeat_interval,
                suppress_redundant=sub.suppress_redundant
            ))
        try:
            for resp in sess.subscribe(
                subscriptions=subs,
                prefix=cnf.subscribe.prefix,
                encoding=cnf.subscribe.encoding,
                mode=cnf.subscribe.mode,
                qos=cnf.subscribe.qos,
                aggregate=cnf.subscribe.allow_aggregation,
            ):
                if resp.sync_response:
                    if cnf.subscribe.mode.lower() == "once":
                        break
                    continue
                cli.write_notification(resp.update, cnf.pretty)
        except GrpcDeadlineExceeded:
            return


if __name__ == "__main__":
    main()
