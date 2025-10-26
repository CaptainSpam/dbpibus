#!/usr/bin/env python3

from desertbus.base_view import BaseView
from desertbus.vst_data import VstData
import time
import adafruit_character_lcd.character_lcd as characterlcd

def _route_page(data: VstData) -> str:
    if data.is_going_to_tucson:
        return "Vegas -> Tucson"
    else:
        return "Tucson -> Vegas"

def _to_next_hour_page(data: VstData) -> str:
    return f"Next: ${data.to_next_hour:,.2f}"

def _hours_bussed_page(data: VstData) -> str:
    return f"Bussed: {data.hours_bussed}:{data.minutes_bussed:02}"

def _total_hours_page(data: VstData) -> str:
    return f"Total hours: {data.total_hours}"

def _pt_cr_page(data: VstData) -> str:
    return f"PT:CR: {data.points}:{data.crashes}"

def _total_splats_page(data: VstData) -> str:
    return f"Bug splats: {data.splats}"

def _total_stops_page(data: VstData) -> str:
    return f"Bus stops: {data.stops}"

_PAGES = [
    _route_page,
    _to_next_hour_page,
    _hours_bussed_page,
    _total_hours_page,
    _pt_cr_page,
    _total_splats_page,
    _total_stops_page,
]

_TOTAL_PAGES = len(_PAGES)
_SERVICE_DOT_MILLIS = 120000

def _needs_service_dot(data: VstData) -> bool:
    time_since_last = (time.time() * 1000) - data.time_fetched
    return time_since_last > _SERVICE_DOT_MILLIS

class NormalView(BaseView):
    """The NormalView, NormalView, NormalView, NORMALVIEEEEEEEEEEEEEW!!! is the
    default "idle" state of the display.  It displays the current donation total
    on the lower half of the display and cycles through different stats on the
    top half."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        super().__init__(lcd)
        # The last time we swapped data pages.
        self._start_time = time.time()

    @property
    def priority(self):
        # NormalView should be the lowest-priority view.  Anything should 
        # outrank it.  Obviously, Python has no concept of a MAX_INT, but still,
        # NormalView should have a higher number than anything else in the
        # system.
        return 9999

    def next_frame(self, data: any) -> bool:
        # This really super needs to have a VstData to do something.
        if not isinstance(data, VstData):
            return False

        # Determine what page we're on based on elapsed time.
        current_page = int(((time.time() - self._start_time) // 4) % _TOTAL_PAGES)
        line1 = _PAGES[current_page](data).center(16)
        line2 = f"${data.donation_total:,.2f}{'.' if _needs_service_dot(data) else ''}".center(16)
        self._display_text(line1, line2)

        # We don't use the frame timer, but still, advance it.
        self._advance_frame_time()
        return False
