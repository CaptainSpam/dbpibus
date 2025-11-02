#!/usr/bin/env python3

"""In-game event-related data and functions."""

from typing import List
from desertbus.simple_animation_view import SimpleAnimationView
from desertbus.vst_data import VstData

POINT_GET_ANIM = [
    (100, "   -            ", "                "),
    (100, "   +            ", "                "),
    (100, "   P|           ", "                "),
    (100, "   P+           ", "                "),
    (100, "   PO-          ", "                "),
    (100, "   PO+          ", "                "),
    (100, "   POI|         ", "                "),
    (100, "   POI+         ", "                "),
    (100, "   POIN-        ", "                "),
    (100, "   POIN+        ", "                "),
    (100, "   POINT |      ", "                "),
    (100, "   POINT +      ", "                "),
    (100, "   POINT G-     ", "                "),
    (100, "   POINT G+     ", "                "),
    (100, "   POINT GE|    ", "                "),
    (100, "   POINT GE+    ", "                "),
    (100, "   POINT GET-   ", "                "),
    (100, "   POINT GET+   ", "                "),
    (500, "   POINT GET!   ", "                "),
    (100, "   POINT GET!   ", "  .             "),
    (100, "   POINT GET!   ", "  +       .     "),
    (100, "   POINT GET!   ", "  *   .   +     "),
    (100, "   POINT GET!   ", "      +   *   . "),
    (100, "   POINT GET!   ", " .    *       + "),
    (100, "   POINT GET!   ", " +      .     * "),
    (100, "   POINT GET!   ", " *      +   .   "),
    (100, "   POINT GET!   ", "    .   *   +   "),
    (100, "   POINT GET!   ", ".   +       *   "),
    (100, "   POINT GET!   ", "+   *  .        "),
    (100, "   POINT GET!   ", "*      +     .  "),
    (100, "   POINT GET!   ", "   .   *     +  "),
    (100, "   POINT GET!   ", "   +      .  *  "),
    (100, "   POINT GET!   ", "   *      +    ."),
    (100, "   POINT GET!   ", "          *    +"),
    (100, "   POINT GET!   ", "               *"),
    (3000,"   POINT GET!   ", "                "),
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
        # TODO: Add the other events.
        if curr_data.points > prev_data.points:
            # POINT GET!
            events.append(SimpleAnimationView(lcd, POINT_GET_ANIM, "Point Get Animation", 6))

    return events
