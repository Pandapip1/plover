import pytest

from plover.output import (
    AutomaticEmulation,
    NullOutput,
    Output,
    create_keyboard_emulation,
)
from plover.registry import Registry


class FakeEmulation(Output):
    """Always supported and available, unless overridden per test."""


class LowPriorityEmulation(FakeEmulation):
    AUTOMATIC_PRIORITY = 10


class UnavailableEmulation(FakeEmulation):
    @classmethod
    def get_missing_requirements(cls):
        return ["pretend this backend can't actually be used right now"]


class ExplodingEmulation(FakeEmulation):
    """Claims to be available, but blows up when actually instantiated --
    e.g. a runtime permission problem that get_missing_requirements() can't
    detect in advance.
    """

    def __init__(self):
        raise OSError("pretend /dev/whatever couldn't be opened")


@pytest.fixture
def registry(monkeypatch):
    registry = Registry()
    monkeypatch.setattr("plover.output.registry", registry)
    return registry


def test_automatic_prefers_lower_priority(registry):
    registry.register_plugin("keyboard_emulation", "Zzz", FakeEmulation)
    registry.register_plugin("keyboard_emulation", "Aaa", LowPriorityEmulation)
    assert [p.name for p in AutomaticEmulation._candidates()] == ["Zzz", "Aaa"]
    assert AutomaticEmulation._resolve() is FakeEmulation


def test_automatic_falls_back_past_unavailable_backend(registry):
    registry.register_plugin("keyboard_emulation", "Preferred", UnavailableEmulation)
    registry.register_plugin("keyboard_emulation", "Fallback", LowPriorityEmulation)
    assert AutomaticEmulation._resolve() is LowPriorityEmulation
    assert isinstance(AutomaticEmulation.create({}), LowPriorityEmulation)


def test_automatic_create_raises_when_nothing_available(registry):
    registry.register_plugin("keyboard_emulation", "Only", UnavailableEmulation)
    with pytest.raises(RuntimeError):
        AutomaticEmulation.create({})


def test_create_keyboard_emulation_happy_path(registry):
    registry.register_plugin("keyboard_emulation", "Automatic", AutomaticEmulation)
    registry.register_plugin("keyboard_emulation", "Real", FakeEmulation)
    assert isinstance(create_keyboard_emulation("Real", {}), FakeEmulation)


def test_create_keyboard_emulation_falls_back_to_null_output_when_nothing_resolves(
    registry, caplog
):
    registry.register_plugin("keyboard_emulation", "Automatic", AutomaticEmulation)
    assert isinstance(create_keyboard_emulation("Automatic", {}), NullOutput)
    assert "failed to start" in caplog.text


def test_create_keyboard_emulation_falls_back_to_null_output_on_unexpected_crash(
    registry, caplog
):
    # Regression: a backend that reports itself available but crashes on
    # instantiation used to crash Plover at startup instead of degrading.
    registry.register_plugin("keyboard_emulation", "Automatic", AutomaticEmulation)
    registry.register_plugin("keyboard_emulation", "Real", ExplodingEmulation)
    result = create_keyboard_emulation("Real", {})
    assert isinstance(result, NullOutput)
    assert "failed to start" in caplog.text
    # NullOutput itself must never raise.
    result.send_string("hello")
    result.send_backspaces(1)
    result.send_key_combination("a(b)")
    result.set_key_press_delay(10)
