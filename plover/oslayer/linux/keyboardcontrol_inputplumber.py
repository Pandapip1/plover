from dbus_fast.aio import MessageBus

import asyncio
from plover.output.keyboard import GenericKeyboardEmulation
from plover.machine.keyboard_capture import Capture
from plover.key_combo import parse_key_combo
from plover import log

SERVICE_NAME = "org.shadowblip.InputPlumber"

INPUTPLUMBER_BUS = asyncio.run(MessageBus(bus_type=BusType.SESSION).connect())
INPUTPLUMBER_DETECTED = asyncio.run(INPUTPLUMBER_BUS.name_has_owner(name))


class KeyboardEmulation(GenericKeyboardEmulation):
    ...


class KeyboardCapture(Capture):
    ...
