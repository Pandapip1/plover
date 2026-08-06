# `plover.output` -- Text output handling

```{py:module} plover.output

```

This module provides a skeleton for customizable text output. By default,
Plover only outputs steno translations through keyboard emulation, but through
the output plugin mechanism it can also be made to output through other
means, such as writing to a file or sending it over the network.

`Output` is also the base class for `"keyboard_emulation"` plugins (see
{doc}`registry`).

````{class} Output

Encapsulates logic for sending keystrokes. Pass an instance of this to
the {class}`StenoEngine<plover.engine.StenoEngine>` when it is initialized.

```{method} send_backspaces(number_of_backspaces: int)
Sends the specified number of backspace keys.
```

```{method} send_string(s: str)
Sends the sequence of keys that would produce the specified string.
```

```{method} send_key_combination(combo_string: str)
Sends the specified key combination. `combo_string` is a string in the
key combo format described in {mod}`plover.key_combo`.
```

```{classmethod} is_supported() -> bool
`False` hides this backend entirely, e.g. a Linux-only backend on Windows.
```

```{classmethod} get_missing_requirements() -> List[str]
Human-readable reasons this backend can't be used right now, e.g. a missing
dependency; empty if it's ready to use.
```

```{classmethod} is_available() -> bool
Whether this backend is supported and has no missing requirements.
```

```{classmethod} get_option_info() -> Dict[str, (T, Function[(str), T])]
Same convention as
{meth}`StenotypeBase.get_option_info()<plover.machine.base.StenotypeBase.get_option_info>`:
`{name: (default, converter)}`.
```

```{classmethod} create(options: dict) -> Output
Creates an instance of this backend from `options` (see
{meth}`get_option_info`). By default just calls the constructor.
```

```{attribute} AUTOMATIC_PRIORITY
:type: int
:value: 0
`AutomaticEmulation` tries backends in ascending order of this value (ties
broken by name). Generic fallbacks should raise it above the default.
```
````

```{class} AutomaticEmulation
Built-in backend, registered as `Automatic`, that picks the first available
backend for the current platform/session, preferring lower
{attr}`AUTOMATIC_PRIORITY` values. Default value of `keyboard_emulation_type`.
```

```{function} resolve_keyboard_emulation(name: str) -> type[Output]
Resolves a configured `keyboard_emulation_type` name to an available backend,
falling back to {class}`AutomaticEmulation`'s pick if `name` is unknown or
unavailable.
```

```{class} NullOutput
No-op backend: translations are processed normally but nothing is typed.
Used by {func}`create_keyboard_emulation` so a broken backend degrades output
instead of blocking startup.
```

```{function} create_keyboard_emulation(name: str, options: dict) -> Output
Resolves and creates the configured `keyboard_emulation_type` backend (see
{func}`resolve_keyboard_emulation`), falling back to {class}`NullOutput`
(and logging) if it fails to start -- e.g. a runtime permission
{meth}`Output.get_missing_requirements` missed.
```
