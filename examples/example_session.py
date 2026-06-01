#!/usr/bin/env python3
"""
Direct ``Session`` usage — preferred when running multiple RPCs against
the same target, since the gRPC channel is reused.

Demonstrates:
  * context-manager lifetime (channel auto-closes on exit)
  * capabilities, get, set (update), once-mode subscribe
  * native error propagation (``grpc.RpcError`` with ``.code()``)
"""

import argparse

import grpc

from gnmi import Session, TLSConfig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="gNMI gRPC target, host:port")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("-p", "--password", default="")
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--tls-ca")
    return parser.parse_args()


def build_tls(args) -> TLSConfig | None:
    if not args.tls_ca:
        return None
    with open(args.tls_ca, "rb") as fh:
        ca = fh.read()
    return TLSConfig(ca_cert=ca, client_cert=None, client_key=None)


def main():
    args = parse_args()
    metadata = {"username": args.username, "password": args.password}
    tls = build_tls(args)

    with Session(
        args.target, metadata=metadata, insecure=args.insecure, tls=tls
    ) as sess:
        caps = sess.capabilities()
        print(f"gNMI version: {caps.gnmi_version}")
        print(f"Encodings: {[e.name for e in caps.supported_encodings]}\n")

        rsp = sess.get(args.paths)
        for notif in rsp.notifications:
            prefix = notif.prefix
            for u in notif.updates:
                print(f"GET {prefix + u.path} = {u.value}")

        try:
            for resp in sess.subscribe(args.paths, mode="once"):
                if resp.sync_response:
                    break
                prefix = resp.update.prefix
                for u in resp.update.updates:
                    print(f"SUB {prefix + u.path} = {u.value}")
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
                raise


if __name__ == "__main__":
    main()
