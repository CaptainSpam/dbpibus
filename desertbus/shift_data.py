#!/usr/bin/env python3

"""Shift-related data and functions."""

from enum import Enum, auto
from datetime import datetime
from zoneinfo import ZoneInfo
from desertbus.simple_animation_view import SimpleAnimationView

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

# Shift animation sequences.
DAWN_GUARD_ANIM = [
    (500, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (500, " DAWN DAWN DAWN ","  DAWN          "),
    (125, " DAWN DAWN DAWN ","  DAWN DA-      "),
    (825, " DAWN DAWN DAWN ","  DAWN DA-DAWN  "),
    (500, " DAWN           ","                "),
    (125, " DAWN DA-       ","                "),
    (825, " DAWN DA-DAWN   ","                "),

    (500, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (500, " DAWN DAWN DAWN ","  DAWN          "),
    (125, " DAWN DAWN DAWN ","  DAWN DA-      "),
    (825, " DAWN DAWN DAWN ","  DAWN DA-DAWN  "),
    (500, " DAWN           ","                "),
    (125, " DAWN DA-       ","                "),
    (825, " DAWN DA-DAWN   ","                "),

    (500, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (125, " DAWN DAWN DA-  ","                "),
    (825, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (125, " DAWN DAWN      "," DA-            "),
    (125, " DAWN DAWN      "," DA-DA-         "),
    (125, " DAWN DAWN      "," DA-DA-DA-      "),
    (825, " DAWN DAWN      "," DA-DA-DA-DAWN  "),

    (250, " DAWN           ","                "),
    (750, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (125, " DAWN DAWN DAWN "," DA-            "),
    (125, " DAWN DAWN DAWN "," DA-DA-         "),
    (125, " DAWN DAWN DAWN "," DA-DA-DA-      "),
    (825, " DAWN DAWN DAWN "," DA-DA-DA-DAWN  "),

    (250, " DAWN           ","                "),
    (750, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (125, " DAWN DAWN DAWN "," DA-            "),
    (825, " DAWN DAWN DAWN "," DA-DAWN        "),
    (500, " DAWN           ","                "),
    (125, " DAWN DA-       ","                "),
    (825, " DAWN DA-DAWN   ","                "),

    (500, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (125, " DAWN DAWN DA-  ","                "),
    (825, " DAWN           ","                "),
    (500, " DAWN DAWN      ","                "),
    (125, " DAWN DAWN      "," DA-            "),
    (125, " DAWN DAWN      "," DA-DA-         "),
    (125, " DAWN DAWN      "," DA-DA-DA-      "),
    (825, " DAWN DAWN      "," DA-DA-DA-DAWN  "),

    (250, " DAWN           ","                "),
    (750, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (125, " DAWN DAWN DAWN "," DA-            "),
    (125, " DAWN DAWN DAWN "," DA-DA-         "),
    (125, " DAWN DAWN DAWN "," DA-DA-DA-      "),
    (825, " DAWN DAWN DAWN "," DA-DA-DA-DAWN  "),

    (250, " DAWN           ","                "),
    (750, " DAWN DAWN      ","                "),
    (500, " DAWN DAWN DAWN ","                "),
    (125, " DAWN DAWN DAWN "," DA-            "),
    (825, " DAWN DAWN DAWN "," DA-DAWN        "),
    (500, " DAWN           ","                "),
    (125, "   DAWN         ","                "),
    (5000,"   DAWN GUARD   ","                "),
]

ZETA_SHIFT_ANIM = [
    (75,  "L               ","                "),
    (75,  "LL              ","                "),
    (75,  "LLL             ","                "),
    (75,  "LLLL            ","                "),
    (75,  "LLLLL           ","                "),
    (75,  "LLLLLL          ","                "),
    (75,  "LLLLLLL         ","                "),
    (75,  "LLLLLLLL        ","                "),
    (75,  "LLLLLLLLL       ","                "),
    (75,  "LLLLLLLLLL      ","                "),
    (75,  "LLLLLLLLLLL     ","                "),
    (75,  "LLLLLLLLLLLL    ","                "),
    (75,  "LLLLLLLLLLLLL   ","                "),
    (75,  "LLLLLLLLLLLLLL  ","                "),
    (75,  "LLLLLLLLLLLLLLL ","                "),
    (75,  "LLLLLLLLLLLLLLLL","                "),
    (350, "Let's           ","                "),
    (350, "Let's get       ","                "),
    (350, "Let's get ready ","                "),
    (200 ,"Let's get ready ","  to            "),
    (1500,"Let's get ready ","  to RUMBLE!!!  "),
    (500, "ZETA            ","            ZETA"),
    (500, "    ZETA        ","        ZETA    "),
    (500, "        ZETA    ","    ZETA        "),
    (500, "            ZETA","ZETA            "),
    (250, "ZETA            ","            ZETA"),
    (250, "ZETAZETA        ","        ZETAZETA"),
    (250, "ZETAZETAZETA    ","    ZETAZETAZETA"),
    (250, "ZETAZETAZETAZETA","ZETAZETAZETAZETA"),
    (250, "    ZETAZETAZETA","ZETAZETAZETA    "),
    (250, "        ZETAZETA","ZETAZETA        "),
    (250, "            ZETA","ZETA            "),
    (250, "                ","                "),
    (250, "ZETA  Z   Z   Z ","  Z   Z   Z   Z "),
    (250, "  Z   Z   Z   Z ","  Z   Z ZETA  Z "),
    (250, "  Z   Z   Z ZETA","  Z   Z   Z   Z "),
    (250, "  Z   Z   Z   Z ","ZETA  Z   Z   Z "),
    (250, "  Z   Z ZETA  Z ","  Z   Z   Z   Z "),
    (250, "  Z   Z   Z   Z ","  Z ZETA  Z   Z "),
    (250, "  Z ZETA  Z   Z ","  Z   Z   Z   Z "),
    (250, "  Z   Z   Z   Z ","  Z   Z   Z ZETA"),
    (250, "    < ZETA >    ", "                "),
    (250, "                ", "   << ZETA >>   "),
    (250, "  <<< ZETA >>>  ", "                "),
    (250, "                ", " <<<< ZETA >>>> "),
    (250, " <<<< ZETA >>>> ", "                "),
    (250, "                ", "  <<< ZETA >>>  "),
    (250, "   << ZETA >>   ", "                "),
    (250, "                ", "    < ZETA >    "),
    (300, "  Y'all         ", "                "),
    (300, "  Y'all ready   ", "                "),
    (150, "  Y'all ready   ", "    for         "),
    (1200,"  Y'all ready   ", "    for this?   "),
    (5000,"   ZETA SHIFT   ", "                "),
]

def make_view_for_shift(lcd, shift: Shift) -> SimpleAnimationView:
    match(shift):
        # TODO: Implement the rest.
        case Shift.DAWN_GUARD:
            return SimpleAnimationView(lcd, DAWN_GUARD_ANIM, "Dawn Transition", 5)
        case Shift.ALPHA_FLIGHT:
            return None
        case Shift.NIGHT_WATCH:
            return None
        case Shift.OMEGA_SHIFT:
            return None
        case Shift.ZETA_SHIFT:
            return SimpleAnimationView(lcd, ZETA_SHIFT_ANIM, "Zeta Transition", 5)
        case _:
            raise ValueError(f"Invalid value passed to make_view_for_shift(): {shift}")
