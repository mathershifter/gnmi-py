# -*- coding: utf-8 -*-

"""
gnmi.entry — thin sync entry point for the `gnmip` console script.

All command-line wiring lives in :mod:`gnmi.cli`; this module just check for
[cli] extra packages and dispatches to the click command group.
"""


def main():

    try:
        from gnmi.cli import cli, load_rc
    except ImportError:
        print("Please install w/ 'gnmi[cli]' to use the CLI")
        exit(1)
    cli.main(default_map=load_rc(), prog_name="gnmip")


if __name__ == "__main__":
    main()
