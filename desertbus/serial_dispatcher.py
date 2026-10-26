#!/usr/bin/env python3

from desertbus.shift_data import Shift
from desertbus.config import IdleLedFade
import logging
import serial

logger = logging.getLogger(__name__)

_ser = None

# These constants all match serial_constants.h on the Pico side of things.
_COMMAND_SET_IDLE_ANIMATION = 'I'
_COMMAND_UPDATE_CONFIG = 'U'

_CONFIG_IDLE_TYPE = 't'

_IDLE_TYPE_OFF = '0'
_IDLE_TYPE_STATIC = '1'
_IDLE_TYPE_SLOW = '2'
_IDLE_TYPE_FAST = '3'

_IDLE_ANIMATION_DAWNGUARD = '0'
_IDLE_ANIMATION_ALPHAFLIGHT = '1'
_IDLE_ANIMATION_NIGHTWATCH = '2'
_IDLE_ANIMATION_ZETASHIFT = '3'
_IDLE_ANIMATION_OMEGASHIFT = '4'

def init_serial():
    """Initializes serial communications.  If serial's already initialized, does
    nothing.  If something goes wrong, SerialException will be raised."""
    global _ser

    if not is_serial_ready():
        _ser = serial.Serial('/dev/serial0', 9600, timeout = 5)

def close_serial():
    """Closes serial communications.  If serial isn't ready, does nothing."""
    global _ser

    if is_serial_ready():
        try:
            _ser.close()
        except:
            pass

    _ser = None

def is_serial_ready() -> bool:
    """Returns true if serial is ready to go, false if it isn't."""
    return _ser is not None

def change_shift(shift: Shift):
    """Sends the command to change the current idle colors for the shift."""
    match(shift):
        case Shift.DAWN_GUARD:
            _dispatch(_COMMAND_SET_IDLE_ANIMATION + _IDLE_ANIMATION_DAWNGUARD)
        case Shift.ALPHA_FLIGHT:
            _dispatch(_COMMAND_SET_IDLE_ANIMATION + _IDLE_ANIMATION_ALPHAFLIGHT)
        case Shift.NIGHT_WATCH:
            _dispatch(_COMMAND_SET_IDLE_ANIMATION + _IDLE_ANIMATION_NIGHTWATCH)
        case Shift.ZETA_SHIFT:
            _dispatch(_COMMAND_SET_IDLE_ANIMATION + _IDLE_ANIMATION_ZETASHIFT)
        case Shift.OMEGA_SHIFT:
            _dispatch(_COMMAND_SET_IDLE_ANIMATION + _IDLE_ANIMATION_OMEGASHIFT)
        case _:
            raise ValueError(f"Invalid value passed to change_shift(): {shift}")

def change_idle_type(fade: IdleLedFade):
    """Sends the command to change the fade type for the LEDs."""
    match(fade):
        case IdleLedFade.OFF:
            _dispatch(_COMMAND_UPDATE_CONFIG + _CONFIG_IDLE_TYPE + _IDLE_TYPE_OFF)
        case IdleLedFade.STATIC:
            _dispatch(_COMMAND_UPDATE_CONFIG + _CONFIG_IDLE_TYPE + _IDLE_TYPE_STATIC)
        case IdleLedFade.SLOW:
            _dispatch(_COMMAND_UPDATE_CONFIG + _CONFIG_IDLE_TYPE + _IDLE_TYPE_SLOW)
        case IdleLedFade.FAST:
            _dispatch(_COMMAND_UPDATE_CONFIG + _CONFIG_IDLE_TYPE + _IDLE_TYPE_FAST)
        case _:
            raise ValueError(f"Invalid value passed to change_idle_type(): {fade}")

def _dispatch(to_write):
    """Dispatches the given string to serial.  You probably want to wrap this in
    a try block, though I don't know what you'd do if something goes wrong."""
    if _ser is not None:
        # Out it goes!
        logger.debug(f'Dispatching to serial: "{to_write}"')
        _ser.write(to_write.encode())
    else:
        logger.error(f'Tried to dispatch "{to_write}" to serial, but _ser was None?')
