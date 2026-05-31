# -*- coding: utf-8 -*-


from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.path import Path, PathElem, split_path, parse_elem

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

def test_path_from_str_empty():
    # Empty input should produce an empty path, not crash.
    p = Path.from_str("")
    assert list(p.elem) == []
    assert p.origin == ""


def test_path_from_str_root_slash_only():
    # "/" is the empty root path — no elements.
    p = Path.from_str("/")
    assert list(p.elem) == []


def test_path_from_str_trailing_slashes_stripped():
    # Trailing slashes shouldn't add empty elements.
    p = Path.from_str("/a/b/")
    assert [e.name for e in p.elem] == ["a", "b"]


def test_path_from_str_round_trips_origin():
    # origin + path round-trip via str/from_str.
    p = Path.from_str("openconfig:/system/config")
    assert p.origin == "openconfig"
    assert [e.name for e in p.elem] == ["system", "config"]
    # And string round-trip is stable.
    assert Path.from_str(str(p)) == p


def test_path_from_str_origin_does_not_swallow_colons_in_values():
    # A ':' inside a key value (e.g. an IPv6-ish key) must not be
    # mistaken for an origin separator.
    p = Path.from_str("/interfaces/interface[name=Ethernet1:1]/state")
    assert p.origin == ""
    assert [e.name for e in p.elem] == ["interfaces", "interface", "state"]
    assert p.elem[1].key == {"name": "Ethernet1:1"}


def test_path_string_round_trip_preserves_backslash_in_key_value():
    # Regression for the parse_elem double-unescape bug discovered while
    # rescinding AUDIT #16. Backslashes inside key values must survive.
    original = Path.from_str(r"/foo[name=a\]b]")
    assert original.elem[0].key == {"name": "a]b"}
    assert Path.from_str(str(original)) == original


def test_path_add():
    tests = [
        (
            Path(elem=[
                    PathElem(name="a"),
                ],
                origin="custom",
                target="something"
            ),
            Path.from_str("b/c"),
            pb.Path(elem=[
                pb.PathElem(name="a"),
                pb.PathElem(name="b"),
                pb.PathElem(name="c"),
            ],
                origin="custom",
                target="something",)
        ),
    ]

    for t in tests:
        base, path, want = t
        p = base + path
        assert p.encode() == want