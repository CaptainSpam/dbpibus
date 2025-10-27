#!/usr/bin/env python3

"""Shift-related data and functions."""

from enum import Enum, auto
from datetime import datetime
from zoneinfo import ZoneInfo

_PACIFIC_ZONEINFO = ZoneInfo('America/Los_Angeles')

class Shift(Enum):
    """Your garden-variety shift enums."""
    DAWN_GUARD = auto()
    ALPHA_FLIGHT = auto()
    NIGHT_WATCH = auto()
    ZETA_SHIFT = auto()
    OMEGA_SHIFT = auto()

# Color constants for the screen.  These don't perfectly align with the "canon"
# colors used on-stream, as those don't really translate well to the LED
# display.
SCREEN_COLORS = {
    Shift.DAWN_GUARD: [80, 10, 0],
    Shift.ALPHA_FLIGHT: [95, 0, 0],
    Shift.NIGHT_WATCH: [20, 20, 90],
    Shift.ZETA_SHIFT: [80, 0, 80],
    Shift.OMEGA_SHIFT: [40, 40, 40],
}

def get_current_shift() -> Shift:
    """Gets the current shift based on the time out on the west coast.  It's
    up to the caller to not call this if it's currently Omega Shift."""
    right_now = datetime.now(_PACIFIC_ZONEINFO)
    if right_now.hour >=0 and right_now.hour < 6:
        return Shift.ZETA_SHIFT
    if right_now.hour >=6 and right_now.hour < 12:
        return Shift.DAWN_GUARD
    if right_now.hour >=12 and right_now.hour < 18:
        return Shift.ALPHA_FLIGHT
    return Shift.NIGHT_WATCH

