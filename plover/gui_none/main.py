from threading import Event

from plover.gui_none.engine import Engine
from plover.machine.keyboard_capture import (
    resolve_keyboard_capture,
    set_active_keyboard_capture,
)
from plover.output import create_keyboard_emulation


def show_error(title, message):
    print(f"{title}: {message}")


def main(config, controller):
    set_active_keyboard_capture(
        resolve_keyboard_capture(config["keyboard_capture_type"])
    )
    engine = Engine(
        config,
        controller,
        create_keyboard_emulation(
            config["keyboard_emulation_type"],
            config["keyboard_emulation_specific_options"],
        ),
    )
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect("quit", quitting.set)
    engine.start()
    try:
        quitting.wait()
    except KeyboardInterrupt:
        engine.quit()
    return engine.join()
