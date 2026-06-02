# -*- coding: utf-8 -*-

from pathlib import Path

from gnmi._env import _coerce_bool, _coerce_list, _coerce_type, _load


def test_coerce_bool_true_strings():
    for s in ("yes", "true", "t", "1", "YES", "True", "T"):
        assert _coerce_bool(s) is True, s


def test_coerce_bool_false_strings():
    for s in ("no", "false", "f", "0", "NO", "False", "", "anything"):
        assert _coerce_bool(s) is False, s


def test_coerce_bool_passes_through_actual_bool():
    assert _coerce_bool(True) is True
    assert _coerce_bool(False) is False


def test_coerce_bool_non_string():
    assert _coerce_bool(1) is True
    assert _coerce_bool(0) is False


def test_coerce_list_passes_through_list():
    assert _coerce_list(["a", "b"]) == ["a", "b"]


def test_coerce_list_splits_string_on_separators():
    assert _coerce_list("a,b") == ["a", "b"]
    assert _coerce_list("a:b") == ["a", "b"]
    assert _coerce_list("a|b") == ["a", "b"]


def test_coerce_list_strips_whitespace():
    assert _coerce_list(" a , b ") == ["a", "b"]


def test_coerce_type_bool():
    assert _coerce_type("true", bool) is True
    assert _coerce_type("false", bool) is False


def test_coerce_type_int():
    assert _coerce_type("42", int) == 42


def test_coerce_type_str():
    assert _coerce_type(42, str) == "42"


def test_coerce_type_none_val():
    assert _coerce_type(None, str) is None


def test_coerce_type_none_typ():
    assert _coerce_type("hello", None) == "hello"


def test_load_returns_env_with_defaults():
    e = _load()
    assert e.GNMIP_USER == "admin"
    assert e.GNMIP_INSECURE is False
    assert e.GNMIP_FORMAT == "pretty"


def test_load_reads_env_var(monkeypatch):
    monkeypatch.setenv("GNMIP_USER", "testuser")
    e = _load()
    assert e.GNMIP_USER == "testuser"


def test_load_coerces_bool_env_var(monkeypatch):
    monkeypatch.setenv("GNMIP_INSECURE", "true")
    e = _load()
    assert e.GNMIP_INSECURE is True


def test_load_coerces_false_bool_env_var(monkeypatch):
    monkeypatch.setenv("GNMIP_INSECURE", "false")
    e = _load()
    assert e.GNMIP_INSECURE is False


def test_load_rc_path_is_list():
    e = _load()
    assert isinstance(e.GNMIP_RC_PATH, list)
    assert all(isinstance(p, Path) for p in e.GNMIP_RC_PATH)
