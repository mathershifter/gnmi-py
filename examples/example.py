#!/usr/bin/env python3

from gnmi import get, subscribe

paths = ["/system"]
target = "192.168.56.103:50010"

for notif in get(target, paths, auth=("admin", "")):
    prefix = notif.prefix

    for u in notif.updates:
        print(f"{prefix + u.path} = {u.value}")

    for d in notif.deletes:
        print(f"{prefix + d} = DELETED")

for notif in subscribe(
    target, paths, auth=("admin", ""), mode="once"):
    prefix = notif.prefix
    for u in notif.updates:
        print(f"{prefix + u.path} = {u.value}")

    for d in notif.deletes:
        print(f"{prefix + d} = __DELETED__")
