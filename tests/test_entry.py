# -*- coding: utf-8 -*-

import sys
from unittest import mock

import pytest


def test_entry_import_error_prints_message_and_exits(capsys):
    with mock.patch.dict(sys.modules, {"gnmi.cli": None}):
        import importlib
        import gnmi.entry as entry_mod

        importlib.reload(entry_mod)

        with pytest.raises(SystemExit) as exc_info:
            entry_mod.main()

        assert exc_info.value.code == 1
        assert "gnmi[cli]" in capsys.readouterr().out
