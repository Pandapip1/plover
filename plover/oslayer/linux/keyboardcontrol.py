from .display_server import DISPLAY_SERVER
from .keyboardcontrol_inputplumber import INPUTPLUMBER_DETECTED

if DISPLAY_SERVER == "x11":
    from .keyboardcontrol_x11 import KeyboardCapture, KeyboardEmulation
elif INPUTPLUMBER_DETECTED:
    from .keyboardcontrol_inputplumber import KeyboardCapture, KeyboardEmulation
else:
    from .keyboardcontrol_uinput import KeyboardCapture, KeyboardEmulation

__all__ = ["KeyboardCapture", "KeyboardEmulation"]
