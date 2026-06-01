#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inspect the shape of a subscribe stream — prints a TSV of
(path, model class, kind) tuples for every prefix element, update, and
error encountered before the first sync_response.
"""

import argparse

from gnmi import Session


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="gNMI gRPC target, host:port")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("-p", "--password", default="")
    parser.add_argument("--insecure", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    metadata = {"username": args.username, "password": args.password}
    results: list[tuple[str, str, str]] = []

    with Session(args.target, metadata=metadata, insecure=args.insecure) as sess:
        for sr in sess.subscribe(args.paths, mode="once"):
            if sr.sync_response:
                break

            prefix = sr.update.prefix
            for _ in prefix.elem:
                results.append((str(prefix), type(prefix.encode()).__name__, "element"))

            if sr.error:
                results.append((str(prefix), type(sr.error.encode()).__name__, "error"))

            for update in sr.update.updates:
                path = prefix + update.path
                for _ in path.elem:
                    results.append((str(path), type(path.encode()).__name__, "element"))
                    break

                if update.value:
                    results.append((str(path), type(update.encode()).__name__, "value"))

    for res in results:
        print(f"{res[0]}\t{res[1]}\t{res[2]}")


if __name__ == "__main__":
    main()
