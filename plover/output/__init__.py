"""Skeleton for customizable text output.

:class:`Output` is also the base class for ``"keyboard_emulation"`` plugins
(see :mod:`plover.registry`).
"""

from __future__ import annotations

from plover import log
from plover.registry import registry


class Output:
    """Output interface."""

    #: :class:`AutomaticEmulation` tries backends in ascending order of this value
    #: (ties broken by name). Generic fallbacks should raise it above the default.
    AUTOMATIC_PRIORITY: int = 0

    def send_backspaces(self, count):
        """Output the given number of backspaces."""
        raise NotImplementedError()

    def send_string(self, string):
        """Output the given string."""
        raise NotImplementedError()

    def send_key_combination(self, combo):
        """Output a sequence of key combinations.

        See `plover.key_combo` for the format of the `combo` string.
        """
        raise NotImplementedError()

    def set_key_press_delay(self, delay_ms):
        """Sets the delay between outputting key press events."""
        raise NotImplementedError()

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
    def create(cls, options: dict) -> "Output":
        """Creates an instance of this backend from `options` (see
        :meth:`get_option_info`). By default just calls the constructor.
        """
        return cls()


class AutomaticEmulation(Output):
    """Picks the first available backend for the current platform/session."""

    @classmethod
    def _candidates(cls):
        candidates = [
            plugin
            for plugin in registry.list_plugins("keyboard_emulation")
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
        return ["no supported keyboard emulation backend is available"]

    @classmethod
    def create(cls, options: dict) -> Output:
        resolved = cls._resolve()
        if resolved is None:
            raise RuntimeError("no supported keyboard emulation backend is available")
        return resolved.create({})


def resolve_keyboard_emulation(name: str) -> type[Output]:
    """Resolves a configured ``keyboard_emulation_type`` name to an available
    backend, falling back to :class:`AutomaticEmulation`'s pick if `name` is
    unknown or unavailable.
    """
    try:
        plugin = registry.get_plugin("keyboard_emulation", name)
    except KeyError:
        plugin = None
    if plugin is not None and plugin.obj.is_available():
        return plugin.obj
    if name != "Automatic":
        log.warning(
            "keyboard emulation backend %r is not available, falling back to automatic selection",
            name,
        )
    return AutomaticEmulation


class NullOutput(Output):
    """No-op backend: translations are processed normally but nothing is
    typed. Used by :func:`create_keyboard_emulation` so a broken backend
    degrades output instead of blocking startup.
    """

    def send_backspaces(self, count):
        pass

    def send_string(self, string):
        pass

    def send_key_combination(self, combo):
        pass

    def set_key_press_delay(self, delay_ms):
        pass


def create_keyboard_emulation(name: str, options: dict) -> Output:
    """Resolves and creates the configured ``keyboard_emulation_type`` backend,
    falling back to :class:`NullOutput` (and logging) if it fails to start --
    e.g. a runtime permission :meth:`Output.get_missing_requirements` missed.
    """
    keyboard_emulation_class = resolve_keyboard_emulation(name)
    try:
        return keyboard_emulation_class.create(options)
    except Exception:
        log.error(
            "keyboard emulation backend %r failed to start; Plover will run "
            "without the ability to output anything until this is fixed and "
            "Plover is restarted",
            keyboard_emulation_class.__name__,
            exc_info=True,
        )
        return NullOutput()
