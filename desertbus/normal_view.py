#!/usr/bin/env python3

from desertbus.base_view import BaseView
from desertbus.vst_data import VstData, needs_service_dot
from desertbus.button_handler import ButtonData
from desertbus.service_credit_view import ServiceCreditView
from desertbus.service_menu_view import ServiceMenuView
import time
import adafruit_character_lcd.character_lcd as characterlcd
import logging

logger = logging.getLogger(__name__)

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

def _run_starts_in(data: VstData) -> str:
    millis_until = data.start_time_millis - (time.time() * 1000)
    if millis_until < 0:
        # The start time has passed, but we don't have the is_live flag yet.
        return "Starting soon..."

    hours = int(millis_until // _MILLIS_PER_HOUR)
    minutes = int((millis_until % _MILLIS_PER_HOUR) // _MILLIS_PER_MINUTE)
    seconds = int((millis_until % _MILLIS_PER_MINUTE) // 1000)

    # We really shouldn't get 1000+ hour differences here, but...
    return f"{"Start" if hours < 1000 else "Go"}: {hours}:{minutes:02d}:{seconds:02d}"

_LIVE_PAGES = [
    _route_page,
    _to_next_hour_page,
    _hours_bussed_page,
    _total_hours_page,
    _pt_cr_page,
    _total_splats_page,
    _total_stops_page,
]

_OFFSEASON_PAGES = [
    _total_hours_page,
    _pt_cr_page,
    _total_splats_page,
    _total_stops_page,
]

_PRESEASON_PAGES = [
    _to_next_hour_page,
    _total_hours_page,
    _run_starts_in,
]

_TOTAL_LIVE_PAGES = len(_LIVE_PAGES)
_TOTAL_OFFSEASON_PAGES = len(_OFFSEASON_PAGES)
_TOTAL_PRESEASON_PAGES = len(_PRESEASON_PAGES)
_LIVE_PAGE_TIME_SECS = 4
_OFFSEASON_PAGE_TIME_SECS = 6
_COUNTUP_ANIMATION_MILLIS = 1000
_MILLIS_PER_MINUTE = 1000 * 60
_MILLIS_PER_HOUR = _MILLIS_PER_MINUTE * 60

class NormalView(BaseView):
    """The NormalView, NormalView, NormalView, NORMALVIEEEEEEEEEEEEEW!!! is the
    default "idle" state of the display.  It displays the current donation total
    on the lower half of the display and cycles through different stats on the
    top half."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        super().__init__(lcd)
        # The last time we swapped data pages.
        logger.info("Initializing NormalView!")
        self._start_time = time.time()

        # The last "stabilized" donation total, meaning the last time a final
        # count was displayed.  This will only be different from the last
        # displayed count or what's in the incoming data when updating to a
        # new value and in the middle of an animation.
        self._last_stabilized_donations = 0
        # The last time we had a stabilized donation total.  This is used to
        # calculate how much we need to increase the amount per frame during an
        # animation.  This initializes to zero and not self._start_time * 1000
        # to make sure we're starting at the first actual frame, not at init.
        self._last_stabilized_time_millis = 0

    @property
    def priority(self):
        # NormalView should be the lowest-priority view.  Anything should 
        # outrank it.  Obviously, Python has no concept of a MAX_INT, but still,
        # NormalView should have a higher number than anything else in the
        # system.
        return 9999

    def _get_displayed_donation_total(self, data: VstData) -> float:
        """Gets the displayed donation total, accounting for any potential
        animation currently active."""
        right_now_millis = time.time() * 1000

        if self._last_stabilized_donations == data.donation_total:
            # We're stabilized; update the counter and return the total.
            self._last_stabilized_time_millis = right_now_millis
            return data.donation_total
        else:
            # Otherwise, an animation is in progress (or we're about to start
            # one).  First, get how much time has elapsed, then how far along we
            # are in the animation.
            elapsed_time = right_now_millis - self._last_stabilized_time_millis
            progress_percent = elapsed_time / _COUNTUP_ANIMATION_MILLIS

            if progress_percent >= 1.0:
                # We've reached the end!  Display the actual total and
                # stabilize.
                logger.info(f'Ending animation at ${data.donation_total}.')
                self._last_stabilized_time_millis = right_now_millis
                self._last_stabilized_donations = data.donation_total
                return data.donation_total
            else:
                # We're animating!  Figure out what needs to be displayed.
                donation_difference = data.donation_total - self._last_stabilized_donations
                fractional_delta = donation_difference * progress_percent
                return round(self._last_stabilized_donations + fractional_delta, 2)

    def handle_buttons(self, data: any, buttons: ButtonData) -> BaseView:
        to_return = None
        if self._previous_buttons is not None:
            if buttons.back and not self._previous_buttons.back:
                to_return = ServiceCreditView(self._lcd)
            elif buttons.select and not self._previous_buttons.select:
                to_return = ServiceMenuView(self._lcd)

        self._previous_buttons = buttons
        return to_return

    def next_frame(self, data: any) -> bool:
        # This really super needs to have a VstData to do something.
        if not isinstance(data, VstData):
            return False

        right_now_millis = time.time() * 1000

        if self._last_stabilized_time_millis == 0:
            # This is the first frame!  Initialize!
            self._last_stabilized_time_millis = right_now_millis

        line1 = ''
        time_delta = time.time() - self._start_time
        # First: Are we in-run?  That determines what pages we show.
        if data.is_live:
            # The page we're on depends on elapsed time.
            current_page = int((time_delta // _LIVE_PAGE_TIME_SECS) % _TOTAL_LIVE_PAGES)
            line1 = _LIVE_PAGES[current_page](data).center(16)
        elif data.start_time_millis > right_now_millis:
            # We can recycle the offseason page timing.
            current_page = int((time_delta // _OFFSEASON_PAGE_TIME_SECS) % _TOTAL_PRESEASON_PAGES)
            line1 = _PRESEASON_PAGES[current_page](data).center(16)
        else:
            current_page = int((time_delta // _OFFSEASON_PAGE_TIME_SECS) % _TOTAL_OFFSEASON_PAGES)
            line1 = _OFFSEASON_PAGES[current_page](data).center(16)

        # Either way, the second line is the donation total.
        line2 = f"${self._get_displayed_donation_total(data):,.2f}{'.' if needs_service_dot(data) else ''}".center(16)

        # Display 'em!
        self._display_text(line1, line2)

        # We don't use the frame timer, but still, advance it.
        self._advance_frame_time()
        return False
