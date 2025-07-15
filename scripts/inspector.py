# -*- coding: utf-8 -*-
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import argparse
from gnmi.session import Session


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("target", help="gNMI gRPC server")
    parser.add_argument("paths", nargs="+")
    return parser.parse_args()


def main():
    args = parse_args()

    metadata = {"username": "admin", "password": ""}

    results = []

    sess = Session(args.target, metadata=metadata)

    sub = sess.subscribe(args.paths)  # ,options=SubscribeOptions(mode="once"))

    for sr in sub:
        if sr.sync_response:
            break

        prefix = sr.update.prefix

        for p in prefix.element:
            results.append((str(prefix), type(p.encode()).__name__, "element"))
            # break

        if sr.error:
            results.append((str(prefix), type(sr.encode()).__name__, "error"))

        for update in sr.update.updates:
            path = prefix + update.path
            for e in path.element:
                results.append((str(path), type(e.encode()).__name__, "element"))
                break

            if update.value:
                results.append((str(path), type(update.encode()).__name__, "value"))

            # print(str(path), update.get_value())

    for res in results:
        print(f"{res[0]}\t{res[1]}\t{res[2]}")


if __name__ == "__main__":
    main()
