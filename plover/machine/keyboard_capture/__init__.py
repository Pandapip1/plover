"""Skeleton for capturing keyboard input to grab steno keystrokes. Actual
implementations are platform-specific, under :mod:`oslayer <plover.oslayer>`.

:class:`Capture` is also the base class for ``"keyboard_capture"`` plugins
(see :mod:`plover.registry`).
"""

from __future__ import annotations

from collections.abc import Sequence

from plover import log
from plover.registry import registry


class Capture:
    """Encapsulates logic for capturing keyboard input. An instance of this is
    used internally by Plover's built-in keyboard plugin.

    Define the :meth:`key_down` and :meth:`key_up` methods below to implement
    custom behavior that gets executed when a key is pressed or released.
    """

    #: :class:`AutomaticCapture` tries backends in ascending order of this value
    #: (ties broken by name). Generic fallbacks should raise it above the default.
    AUTOMATIC_PRIORITY: int = 0

    def start(self) -> None:
        """Start collecting keyboard input."""
        raise NotImplementedError()

    def cancel(self) -> None:
        """Stop collecting keyboard input."""
        raise NotImplementedError()

    def suppress(self, suppressed_keys: Sequence[str] = ()) -> None:
        """Suppresses the specified keys, preventing them from returning any
        output through regular typing. This allows us to intercept keyboard
        events when using keyboard input.
        """
        raise NotImplementedError()

    # Callbacks for keyboard press/release events.
    def key_down(self, key: str) -> None:
        """Notifies Plover that a key was pressed down."""
        return

    def key_up(self, key: str) -> None:
        """Notifies Plover that a key was released."""
        return

    @classmethod
    def is_supported(cls) -> bool:
        """False hides this backend entirely, e.g. a Linux-only backend on Windows."""
        return True

    @classmethod
    def get_missing_requirements(cls) -> list[str]:
        """Human-readable reasons this backend can't be used right now, e.g. a missing dependency."""
        return []

    @classmethod
    def is_available(cls) -> bool:
        return cls.is_supported() and not cls.get_missing_requirements()

    @classmethod
    def get_option_info(cls) -> dict:
        """Same convention as StenotypeBase.get_option_info: ``{name: (default, converter)}``."""
        return {}

    @classmethod
    def create(cls, options: dict) -> "Capture":
        """Creates an instance of this backend from `options` (see
        :meth:`get_option_info`). By default just calls the constructor.
        """
        return cls()


class AutomaticCapture(Capture):
    """Picks the first available backend for the current platform/session."""

    @classmethod
    def _candidates(cls):
        candidates = [
            plugin
            for plugin in registry.list_plugins("keyboard_capture")
            if plugin.obj is not cls and plugin.obj.is_supported()
        ]
        return sorted(
            candidates, key=lambda plugin: (plugin.obj.AUTOMATIC_PRIORITY, plugin.name)
        )

    @classmethod
    def _resolve(cls):
        for plugin in cls._candidates():
            if plugin.obj.is_available():
                return plugin.obj
        return None

    @classmethod
    def get_missing_requirements(cls) -> list[str]:
        if cls._resolve() is not None:
            return []
        return ["no supported keyboard capture backend is available"]

    @classmethod
    def create(cls, options: dict) -> Capture:
        resolved = cls._resolve()
        if resolved is None:
            raise RuntimeError("no supported keyboard capture backend is available")
        return resolved.create({})


def resolve_keyboard_capture(name: str) -> type[Capture]:
    """Resolves a configured ``keyboard_capture_type`` name to an available
    backend, falling back to :class:`AutomaticCapture`'s pick if `name` is
    unknown or unavailable.
    """
    try:
        plugin = registry.get_plugin("keyboard_capture", name)
    except KeyError:
        plugin = None
    if plugin is not None and plugin.obj.is_available():
        return plugin.obj
    if name != "Automatic":
        log.warning(
            "keyboard capture backend %r is not available, falling back to automatic selection",
            name,
        )
    return AutomaticCapture


_active_keyboard_capture: type[Capture] | None = None


def set_active_keyboard_capture(keyboard_capture: type[Capture]) -> None:
    global _active_keyboard_capture
    _active_keyboard_capture = keyboard_capture


def get_active_keyboard_capture() -> type[Capture]:
    if _active_keyboard_capture is None:
        raise RuntimeError("no active keyboard capture backend has been set")
    return _active_keyboard_capture
