# -*- coding: utf-8 -*-


import pytest

from gnmi.util import escape_string, oneof, parse_duration


def test_parse_duration():
    tests = {
        "1ns": 1,
        "1us": 1000,
        "1ms": 1_000_000,
        "1s": 1_000_000_000,
        "1m": 60_000_000_000,
        "1586ms": 1_586_000_000,
    }
    for s, want in tests.items():
        assert parse_duration(s) == want


# ---------------------------------------------------------------------------
# escape_string (AUDIT.md Testing Nit)
# ---------------------------------------------------------------------------


def test_escape_string_passthrough_when_no_metachars():
    assert escape_string("plain", "/") == "plain"


def test_escape_string_escapes_each_target_char():
    assert escape_string("a/b/c", "/") == "a\\/b\\/c"


def test_escape_string_escapes_backslash_in_addition_to_targets():
    # Backslash is always escaped — needed so the consumer can unambiguously
    # tell a literal backslash from an escape lead.
    assert escape_string("a\\b", "/") == "a\\\\b"


def test_escape_string_supports_multi_char_escape_set():
    # The `escape` arg is treated as a set of characters (every char in
    # the string is added to the metachar list).
    assert escape_string("a]b/c", "]/") == "a\\]b\\/c"


# ---------------------------------------------------------------------------
# oneof error paths (AUDIT.md Testing #6)
# ---------------------------------------------------------------------------


def test_oneof_zero_set_raises():
    with pytest.raises(ValueError):
        oneof(None, None)


def test_oneof_multiple_set_raises():
    with pytest.raises(ValueError):
        oneof("a", "b")


def test_oneof_single_set_returns_index():
    assert oneof("only", None, None) == 0
    assert oneof(None, "only", None) == 1
    assert oneof(None, None, "only") == 2
