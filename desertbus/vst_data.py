#!/usr/bin/env python3

from dataclasses import dataclass
from desertbus.shift_data import Shift
import time

_SERVICE_DOT_MILLIS = 120000

@dataclass(frozen=True)
class VstData:
    """The various data useful for display.  NOT just the raw API JSON blob. """

    # The time (millis since the epoch) this data was fetched.
    time_fetched: int = 0

    # The current donation total.
    donation_total: float = 0.0
    # Amount needed to reach the next hour.
    to_next_hour: float = 0.0

    # Hours bussed (as a whole number; see minutes_bussed).
    hours_bussed: int = 0
    # Minutes bussed within the current hour; will be 0-59.
    minutes_bussed: int = 0
    # Total hours that will be bussed, given current donations.
    total_hours: int = 0

    # Current bus odometer reading.
    odometer: float = 70109.3

    # Points scored this run.
    points: int = 0
    # Crashes experienced this run.
    crashes: int = 0
    # Bugs splatted this run.
    splats: int = 0
    # Successful bus stops this run.
    stops: int = 0

    # The start time of this run, in UNIX timestamp millis.  May be in the
    # future.
    start_time_millis: int = 0

    # The current shift.  Useful for light shows and transition animations.
    current_shift: Shift = Shift.DAWN_GUARD

    # True if Desert Bus for Hope is currently live, False if the event is over
    # for the year.
    is_live: bool = False
    # True if Omega Shift is live, False if not, None if there was an error
    # fetching it (likely meaning we just retain the previous value).
    is_omega_shift: bool = False
    # True if the bus is en route to Tucson, False if the bus is en route to
    # Las Vegas.
    is_going_to_tucson: bool = False

def needs_service_dot(data: VstData) -> bool:
    time_since_last = (time.time() * 1000) - data.time_fetched
    return time_since_last > _SERVICE_DOT_MILLIS
