# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.path import Path, split_path, parse_elem

def test_split_path():
    tests = {
        r"/a/b/c": ("", ["a", "b", "c"]),
        r"openconfig:interfaces/interface[name=Ethernet1/2/3]/state": (r"openconfig", [r"interfaces", r"interface[name=Ethernet1/2/3]", r"state"]),
        r"/interfaces/interface[name=Ethernet1/2/3]/state/counters": (r"", [r"interfaces", r"interface[name=Ethernet1/2/3]", r"state", r"counters"]),
        r"/network-instances/network-instance[name=DEFAULT]/protocols/protocol[identifier=ISIS][name=65497]":
            (r"", [r"network-instances", r"network-instance[name=DEFAULT]", r"protocols", r"protocol[identifier=ISIS][name=65497]"]),
        r"/foo[name=\]]": (r"", [r"foo[name=\]]"]),
        r"/foo[name=[]": (r"", [r"foo[name=[]"]),
        r"/foo[name=[\\\]]": (r"", [r"foo[name=[\\\]]"]),
    }

    for p, want in tests.items():
        got = split_path(p)
        assert want == got

def test_parse_elem():
    tests = {
        r"interfaces": ("interfaces", {}),
        r"interface[name=Ethernet1/2/3]": ("interface", {"name": "Ethernet1/2/3"}),
        r"protocol[identifier=ISIS][name=65497]": ("protocol", {"identifier": "ISIS", "name": "65497"}),
        r"foo[name=\]]": ("foo", {"name": "]"}),
        r"foo[name=[]": ("foo", {"name": "["}),
        r"foo[name=\\\]]": ("foo", {"name": r"\]"}),
    }

    for e, want in tests.items():
        got = parse_elem(e)
        assert want == got

def test_path():
    tests = [
        (
            r"/a/b/c",
            pb.Path(elem=[
                pb.PathElem(name="a"),
                pb.PathElem(name="b"),
                pb.PathElem(name="c"),
            ])
        ),
        (
            r"openconfig:/interfaces/interface[name=Ethernet1/2/3]/state",
            pb.Path(
                origin="openconfig",
                elem=[
                    pb.PathElem(name="interfaces"),
                    pb.PathElem(name="interface", key={
                        "name": "Ethernet1/2/3"
                    }),
                    pb.PathElem(name="state"),
                ],
            )
        ),
        (
            r"/interfaces/interface[name=Ethernet1/2/3]/state/counters",
            pb.Path(
                elem=[
                    pb.PathElem(name="interfaces"),
                    pb.PathElem(name="interface", key={"name": "Ethernet1/2/3"}),
                    pb.PathElem(name="state"),
                    pb.PathElem(name="counters")
            ])

        ),
        (
            r"/network-instances/network-instance[name=DEFAULT]/protocols/protocol[identifier=ISIS][name=65497]",
            pb.Path(
                elem=[
                    pb.PathElem(name="network-instances"),
                    pb.PathElem(name="network-instance", key={"name": "DEFAULT"}),
                    pb.PathElem(name="protocols"),
                    pb.PathElem(name="protocol", key={"identifier": "ISIS", "name": "65497"}),
                ]
            )
        ),
        (
            r"/foo[name=\]]",
            pb.Path(
                elem=[
                    pb.PathElem(name="foo", key={"name": "]"})
                ]
            )
        ),
        (
            r"/foo[name=[]",
            pb.Path(elem=[
                pb.PathElem(name="foo", key={"name": "["})
            ])
        ),
        (
            r"/foo[name=[\\\]]",
            pb.Path(elem=[
                pb.PathElem(name="foo", key={"name": r"[\]"})
            ])
        ),
        (
            r"cli:/show running-config",
            pb.Path(
                origin="cli",
                elem=[
                    pb.PathElem(name="show running-config")
                ]
            )
        ),
    ]

    for t in tests:
        p, want = t
        assert Path.from_str(p).encode() == want
