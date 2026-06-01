#!/usr/bin/env python3
"""
High-level gnmi-py API quick tour.

Uses the top-level ``get`` / ``subscribe`` helpers from ``gnmi.api`` —
each opens a short-lived ``Session`` for one RPC. For multi-RPC work,
use ``Session`` directly as a context manager (see ``example_session.py``).
"""

from gnmi import get, subscribe

TARGET = "192.168.56.103:6030"
PATHS = ["/system"]
AUTH = ("admin", "")


def print_notification(notif):
    prefix = notif.prefix
    for u in notif.updates:
        print(f"{prefix + u.path} = {u.value}")
    for d in notif.deletes:
        print(f"{prefix + d} = DELETED")


# --- one-shot get -----------------------------------------------------------
print("=== get ===")
for notif in get(TARGET, PATHS, auth=AUTH, insecure=True):
    print_notification(notif)

# --- once-mode subscribe ----------------------------------------------------
print("\n=== subscribe (once) ===")
for notif in subscribe(TARGET, PATHS, auth=AUTH, insecure=True, mode="once"):
    print_notification(notif)
