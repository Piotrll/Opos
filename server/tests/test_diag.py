# python
import types
import pytest
from server.diag import Diag
import psutil
import time

class _Simple:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_run_boot_diag_collects_samples_and_respects_max_iterations(monkeypatch):
    # Prepare deterministic sequences
    cpu_values = [10.0, 20.0, 30.0]
    def fake_cpu_percent(interval=0):
        return cpu_values.pop(0)

    mem_sequence = [
        _Simple(percent=30.0, used=300),
        _Simple(percent=40.0, used=400),
        _Simple(percent=50.0, used=500),
    ]
    def fake_virtual_memory():
        return mem_sequence.pop(0)

    disk_sequence = [
        _Simple(percent=5.0, used=50),
        _Simple(percent=6.0, used=60),
        _Simple(percent=7.0, used=70),
    ]
    def fake_disk_usage(path):
        return disk_sequence.pop(0)

    # time.time returns incrementing timestamps
    t = {"now": 1000.0}
    def fake_time():
        v = t["now"]
        t["now"] += 1.0
        return v

    # Patch target functions
    monkeypatch.setattr(psutil, "cpu_percent", fake_cpu_percent)
    monkeypatch.setattr(psutil, "virtual_memory", fake_virtual_memory)
    monkeypatch.setattr(psutil, "disk_usage", fake_disk_usage)
    monkeypatch.setattr(time, "time", fake_time)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    d = Diag(root_path="/")  # root_path not used because disk_usage is patched
    samples = d.run_boot_diag(max_iterations=3, sleep_interval=0)

    assert isinstance(samples, list)
    assert len(samples) == 3

    # Validate fields and values for each sample
    expected_cpu = [10.0, 20.0, 30.0]
    expected_mem_percent = [30.0, 40.0, 50.0]
    expected_mem_used = [300, 400, 500]
    expected_disk_percent = [5.0, 6.0, 7.0]
    expected_disk_used = [50, 60, 70]
    expected_timestamps = [1000.0, 1001.0, 1002.0]

    for i, s in enumerate(samples):
        assert "cpu_percent" in s
        assert "memory_percent" in s
        assert "memory_used" in s
        assert "disk_percent" in s
        assert "disk_used" in s
        assert "timestamp" in s

        assert s["cpu_percent"] == expected_cpu[i]
        assert s["memory_percent"] == expected_mem_percent[i]
        assert s["memory_used"] == expected_mem_used[i]
        assert s["disk_percent"] == expected_disk_percent[i]
        assert s["disk_used"] == expected_disk_used[i]
        assert s["timestamp"] == expected_timestamps[i]

def test_init_with_boot_calls_run_boot_diag_and_prints(monkeypatch, capsys):
    # Make run_boot_diag deterministic and fast
    def fake_run_boot_diag(self):
        return [{"ok": True}]
    monkeypatch.setattr(Diag, "run_boot_diag", fake_run_boot_diag)

    # Instantiate with boot=True 
    Diag(boot=True)

    captured = capsys.readouterr()
    # The printed representation
    assert "[{'ok': True}]" in captured.out
    