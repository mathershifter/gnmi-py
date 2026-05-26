# -*- coding: utf-8 -*-
# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
gnmi.entry — thin sync entry point for the `gnmip` console script.

All command-line wiring lives in :mod:`gnmi.cli`; this module just hooks
up the SIGINT handler and dispatches to the click command group.
"""
import signal
import sys


def signal_handler(*_, **__):
    sys.exit(0)


def main() -> None:
    # Install the SIGINT handler only when actually invoked. Installing at
    # import time would clobber the handler for anyone who imports
    # gnmi.entry (notably tests and library consumers).
    signal.signal(signal.SIGINT, signal_handler)

    try:
        from gnmi.cli import cli, load_rc
    except ImportError:
        print("Please install w/ 'gnmi[cli]' to use the CLI")
        sys.exit(1)

    # rc file -> click defaults. --config FILE (handled by the group's
    # configuration_option) layers on top; explicit CLI args layer above
    # that.
    cli.main(default_map=load_rc(), prog_name="gnmip")


if __name__ == "__main__":
    main()
