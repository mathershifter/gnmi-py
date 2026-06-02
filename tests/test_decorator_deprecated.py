# -*- coding: utf-8 -*-

import warnings

import pytest

from gnmi.decorator import deprecated
from gnmi.exceptions import GnmiDeprecationError
from gnmi._env import env


def test_deprecated_function_emits_warning():
    @deprecated("gone")
    def fn():
        return 42

    with pytest.warns(DeprecationWarning, match="gone"):
        assert fn() == 42


def test_deprecated_function_custom_warning_cls():
    @deprecated("old", cls=PendingDeprecationWarning)
    def fn():
        pass

    with pytest.warns(PendingDeprecationWarning, match="old"):
        fn()


def test_deprecated_function_preserves_name():
    @deprecated("x")
    def my_func():
        pass

    assert my_func.__name__ == "my_func"


def test_deprecated_class_emits_warning_on_init():
    @deprecated("old class")
    class Foo:
        def __init__(self, x):
            self.x = x

    with pytest.warns(DeprecationWarning, match="old class"):
        f = Foo(99)
    assert f.x == 99


def test_deprecated_class_preserves_init_args():
    @deprecated("x")
    class Bar:
        def __init__(self, a, b, kw=None):
            self.a = a
            self.b = b
            self.kw = kw

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        b = Bar(1, 2, kw="yes")
    assert b.a == 1
    assert b.b == 2
    assert b.kw == "yes"


def test_deprecated_function_raises_when_no_deprecated(monkeypatch):
    monkeypatch.setattr(env, "GNMIP_NO_DEPRECATED", True)

    @deprecated("removed")
    def fn():
        pass

    with pytest.raises(GnmiDeprecationError):
        fn()


def test_deprecated_class_raises_when_no_deprecated(monkeypatch):
    monkeypatch.setattr(env, "GNMIP_NO_DEPRECATED", True)

    @deprecated("removed")
    class Cls:
        pass

    with pytest.raises(GnmiDeprecationError):
        Cls()
