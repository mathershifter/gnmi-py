#!/usr/bin/env python3
"""
``AsyncSession`` — the asyncio equivalent of ``Session``. Same surface
(``capabilities`` / ``get`` / ``set`` / ``subscribe``), driven via
``async with`` and ``async for``.

The CLI (`gnmip`) is built on top of this.
"""
import argparse
import asyncio

import grpc

from gnmi import AsyncSession


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="gNMI gRPC target, host:port")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("-p", "--password", default="")
    parser.add_argument("--insecure", action="store_true")
    return parser.parse_args()


async def amain(args) -> None:
    metadata = {"username": args.username, "password": args.password}

    async with AsyncSession(args.target, metadata=metadata, insecure=args.insecure) as sess:
        caps = await sess.capabilities()
        print(f"gNMI version: {caps.gnmi_version}\n")

        rsp = await sess.get(args.paths)
        for notif in rsp.notifications:
            prefix = notif.prefix
            for u in notif.updates:
                print(f"GET {prefix + u.path} = {u.value}")

        try:
            async for resp in sess.subscribe(args.paths, mode="once"):
                if resp.sync_response:
                    break
                prefix = resp.update.prefix
                for u in resp.update.updates:
                    print(f"SUB {prefix + u.path} = {u.value}")
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
                raise


if __name__ == "__main__":
    asyncio.run(amain(parse_args()))
