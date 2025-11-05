#!/usr/bin/env python3

"""In-game event-related data and functions."""

from typing import List
from enum import Enum, auto
from desertbus.simple_animation_view import SimpleAnimationView
from desertbus.vst_data import VstData

class Event(Enum):
    """The events."""
    POINT = auto()
    CRASH = auto()
    SPLAT = auto()
    STOP = auto()

POINT_GET_ANIM = [
    (100, "   -            ","                "),
    (100, "   +            ","                "),
    (100, "   P|           ","                "),
    (100, "   P+           ","                "),
    (100, "   PO-          ","                "),
    (100, "   PO+          ","                "),
    (100, "   POI|         ","                "),
    (100, "   POI+         ","                "),
    (100, "   POIN-        ","                "),
    (100, "   POIN+        ","                "),
    (100, "   POINT |      ","                "),
    (100, "   POINT +      ","                "),
    (100, "   POINT G-     ","                "),
    (100, "   POINT G+     ","                "),
    (100, "   POINT GE|    ","                "),
    (100, "   POINT GE+    ","                "),
    (100, "   POINT GET-   ","                "),
    (100, "   POINT GET+   ","                "),
    (500, "   POINT GET!   ","                "),
    (100, "   POINT GET!   ","  .             "),
    (100, "   POINT GET!   ","  +       .     "),
    (100, "   POINT GET!   ","  *   .   +     "),
    (100, "   POINT GET!   ","      +   *   . "),
    (100, "   POINT GET!   "," .    *       + "),
    (100, "   POINT GET!   "," +      .     * "),
    (100, "   POINT GET!   "," *      +   .   "),
    (100, "   POINT GET!   ","    .   *   +   "),
    (100, "   POINT GET!   ",".   +       *   "),
    (100, "   POINT GET!   ","+   *  .        "),
    (100, "   POINT GET!   ","*      +     .  "),
    (100, "   POINT GET!   ","   .   *     +  "),
    (100, "   POINT GET!   ","   +      .  *  "),
    (100, "   POINT GET!   ","   *      +    ."),
    (100, "   POINT GET!   ","          *    +"),
    (100, "   POINT GET!   ","               *"),
    (3000,"   POINT GET!   ","                "),
]

BUG_SPLAT_ANIM = [
    (100, "        S       ","                "),
    (100, "        SP      ","                "),
    (100, "     G  SPL     ","                "),
    (100, "    UG  SPLA    ","                "),
    (100, "   BUG  SPLAT   ","                "),
    (100, "  *BUG  SPLAT*  ","                "),
    (100, " * BUG  SPLAT * ","                "),
    (100, "*  BUG  SPLAT  *","                "),
    (1000,"   BUG  SPLAT   ","                "),
    (300, "   BUG  SPLAT   ","     |          "),
    (100, "   BUG  SPLAT   ","     |      |   "),
    (200, "   BUG  SPLAT   ","     *      |   "),
    (300, "   BUG  SPLAT   ","     *      *   "),
    (400, "   BUG  SPLAT   ","     @   |  *   "),
    (2600,"   BUG  SPLAT   ","   | @   *  @   "),
]

BUS_STOP_ANIM = [
    (100, "               B","                "),
    (150, "              BU","                "),
    (400, "             BUS","                "),
    (250, "            BUS ","                "),
    (100, "           BUS S","                "),
    (100, "         BUS STO","                "),
    (100, "       BUS STOP ","                "),
    (100, "     BUS STOP   ","                "),
    (3000,"    BUS STOP    ","                "),
    (100, "     BUS STOP   ","                "),
    (100, "       BUS STOP ","                "),
    (100, "         BUS STO","                "),
    (100, "           BUS S","                "),
    (250, "            BUS ","                "),
    (400, "             BUS","                "),
    (150, "              BU","                "),
    (100, "               B","                "),
    (100, "                ","                "),
]

CRASH_ANIM = [
    (100, "A              S","                "),
    (100, "RA            SH","                "),
    (100, "CRA          SH!","                "),
    (100, " CRA        SH! ","                "),
    (100, "  CRA      SH!  ","                "),
    (100, "   CRA    SH!   ","                "),
    (100, "    CRA  SH!    ","                "),
    (100, "     CRASH!     ","                "),
    (100, "    <CRASH!>    ","                "),
    (100, "   <<CRASH!>>   ","                "),
    (100, "  << CRASH! >>  ","       .        "),
    (100, " <<  CRASH!  >> ","      .  *      "),
    (100, "<<  +CRASH!   >>","     .    *     "),
    (100, "<  + CRASH!    >","    .      *    "),
    (100, "  +  CRASH!.    ","   .        *   "),
    (100, " +   CRASH! .   ","  .          *  "),
    (100, "+    CRASH!  .  "," .            * "),
    (100, "     CRASH!   . ",".              *"),
    (100, "     CRASH!    .","                "),
    (3000,"     CRASH!     ","                "),
]

def make_views_for_events(lcd, prev_data: VstData, curr_data: VstData) -> List[SimpleAnimationView]:
    """Makes potentially multiple views for in-game events, depending on the
    differences in stats between two points in time.  This is a list because you
    never know when Ian will successfully make a bus stop and then crash the bus
    within the thirty seconds it takes for a data fetch.

    Returns an empty list if no events have happened."""
    events: List[SimpleAnimationView] = []

    # Only do this if we have both previous and current data.
    if prev_data is not None and curr_data is not None:
        # We'll use priorities of 6-9 for events.  Shift changes should still
        # come first.
        if curr_data.points > prev_data.points:
            # POINT GET!
            events.append(make_view_for_event(lcd, Event.POINT, 6))
        if curr_data.splats > prev_data.splats:
            # Bug splat!
            events.append(make_view_for_event(lcd, Event.SPLAT, 7))
        if curr_data.stops > prev_data.stops:
            # Bus stop!
            events.append(make_view_for_event(lcd, Event.STOP, 8))
        if curr_data.crashes > prev_data.crashes:
            # CRASH!  This should get lowest priority, as it'll no doubt be the
            # last thing that happens in any potential cluster of multiple
            # simultaneous events.
            events.append(make_view_for_event(lcd, Event.CRASH, 9))

    return events

def make_view_for_event(lcd, event: Event, priority: int) -> SimpleAnimationView:
    """Makes a single event view."""
    match event:
        case Event.POINT:
            return SimpleAnimationView(lcd, POINT_GET_ANIM, "Point Get Animation", priority)
        case Event.CRASH:
            return SimpleAnimationView(lcd, CRASH_ANIM, "Crash Animation", priority)
        case Event.SPLAT:
            return SimpleAnimationView(lcd, BUG_SPLAT_ANIM, "Bug Splat Animation", priority)
        case Event.STOP:
            return SimpleAnimationView(lcd, BUS_STOP_ANIM, "Bus Stop Animation", priority)
        case _:
            raise ValueError(f'Invalid event enum {event}!')
