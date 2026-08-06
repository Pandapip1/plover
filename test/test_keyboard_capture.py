import pytest

from plover.machine.keyboard_capture import AutomaticCapture, Capture
from plover.registry import Registry


class FakeCapture(Capture):
    """Always supported and available, unless overridden per test."""


class LowPriorityCapture(FakeCapture):
    AUTOMATIC_PRIORITY = 10


class UnavailableCapture(FakeCapture):
    @classmethod
    def get_missing_requirements(cls):
        return ["pretend this backend can't actually be used right now"]


@pytest.fixture
def registry(monkeypatch):
    registry = Registry()
    monkeypatch.setattr("plover.machine.keyboard_capture.registry", registry)
    return registry


def test_automatic_prefers_lower_priority(registry):
    # Regression: Automatic used to just sort alphabetically, so a generic
    # fallback could beat a better match purely by name.
    registry.register_plugin("keyboard_capture", "Zzz", FakeCapture)
    registry.register_plugin("keyboard_capture", "Aaa", LowPriorityCapture)
    assert [p.name for p in AutomaticCapture._candidates()] == ["Zzz", "Aaa"]
    assert AutomaticCapture._resolve() is FakeCapture


def test_automatic_falls_back_past_unavailable_backend(registry):
    registry.register_plugin("keyboard_capture", "Preferred", UnavailableCapture)
    registry.register_plugin("keyboard_capture", "Fallback", LowPriorityCapture)
    assert AutomaticCapture._resolve() is LowPriorityCapture
    assert isinstance(AutomaticCapture.create({}), LowPriorityCapture)


def test_automatic_create_raises_when_nothing_available(registry):
    registry.register_plugin("keyboard_capture", "Only", UnavailableCapture)
    with pytest.raises(RuntimeError):
        AutomaticCapture.create({})
