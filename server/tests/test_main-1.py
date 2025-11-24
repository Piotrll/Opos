# ...existing code...
import os
import sys
from pathlib import Path

import pytest

import server.main as mainmod

class DummyLog:
    def __init__(self, *a, **k):
        pass

def _norm_path(p: str) -> str:
    return os.path.normcase(os.path.normpath(p))

def _setup_mocks(monkeypatch):
    # Prevent arg parsing / logger side effects
    monkeypatch.setattr(mainmod.argHandle, "decode_args", lambda args: {})
    monkeypatch.setattr(mainmod.logg, "MainLog", DummyLog)

def test_base_dir_not_frozen(monkeypatch):
    _setup_mocks(monkeypatch)
    # ensure not frozen
    monkeypatch.setattr(sys, "frozen", False, raising=False)

    inst = mainmod.Main([])

    # expected is the folder containing server/main.py
    expected = os.path.dirname(os.path.abspath(mainmod.__file__))
    assert _norm_path(inst.diag.root_path) == _norm_path(expected)

def test_base_dir_when_frozen_uses_executable_parent(monkeypatch, tmp_path):
    _setup_mocks(monkeypatch)

    # prepare a fake executable path (no need to actually create the file)
    fake_exe = str(tmp_path / "sub" / "dir" / "app.exe")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", fake_exe, raising=False)

    inst = mainmod.Main([])

    expected = os.path.dirname(os.path.abspath(fake_exe))
    assert _norm_path(inst.diag.root_path) == _norm_path(expected)
# ...existing code...

