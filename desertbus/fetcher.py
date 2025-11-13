#!/usr/bin/env python3

import time
import json
import urllib.request
import logging
from urllib.error import HTTPError
from datetime import datetime
from desertbus import donation_converter
from desertbus.vst_data import VstData
from desertbus.shift_data import Shift, get_current_shift

logger = logging.getLogger(__name__)

_URL_PREFIX = 'https://vst.ninja/'
_IS_OMEGA_URL = f'{_URL_PREFIX}Resources/isitomegashift.html'

# Field names are mostly tentative.
_JSON_STATS_CATEGORY = "Stats"

_JSON_GAME_DATA_CATEGORY = "Game Data"
_JSON_ODOMETER = 'Desert Bus: Current Mileage'
_JSON_POINTS = 'Desert Bus: Total Points'
_JSON_CRASHES = 'Desert Bus: Total Crashes'
_JSON_SPLATS = 'Desert Bus: Total Bug Splats'
_JSON_STOPS = 'Desert Bus: Total Bus Stops'

_JSON_YEAR_DATA_CAGEGORY = "Year Data"
_JSON_IS_LIVE = 'Run Live'
_JSON_RUN_START_TIME = 'Year Start UNIX-Time'

_JSON_DONATION_DATA_CATEGORY = "Donation Data"
_JSON_DONATIONS = 'Total Raised'

_YEAR_OFFSET = 2006
# Floats should be okay here, unless Python has issues with the hundredths digit.
# It might, you never know.
_ODOMETER_OFFSET = 70109.3
_MILES_TO_VEGAS = 360
_MILLIS_PER_MINUTE = 1000 * 60
_MILLIS_PER_HOUR = _MILLIS_PER_MINUTE * 60
_TIMEOUT_SECS = 20

def _make_stats_url_for_year(year):
    numbered_run = year - _YEAR_OFFSET
    return f'{_URL_PREFIX}DB{numbered_run}/data/DB{numbered_run}_stats_v2.json'

def get_current_stats() -> VstData:
    """Fetches the current stats from the VST."""
    # First, try for this year.
    year = datetime.now().year
    json_data = None

    try:
        logger.debug(f'Fetching data for {year}...')
        with urllib.request.urlopen(_make_stats_url_for_year(year), timeout=_TIMEOUT_SECS) as response:
            json_data = json.loads(response.read())
    except HTTPError as e:
        if e.code == 404:
            # Whoops, it doesn't exist yet.  Back off a year.  If THIS doesn't
            # work, then we throw.
            logger.debug(f'{year} has no data yet, trying again with {year - 1}...')
            with urllib.request.urlopen(_make_stats_url_for_year(year - 1), timeout=_TIMEOUT_SECS) as response:
                json_data = json.loads(response.read())
        else:
            # Any other error, we throw it back.
            raise e

    # Also, check if it's omega or not.
    omega = None
    try:
        logger.debug('Checking if Omega Shift is live...')
        with urllib.request.urlopen(_IS_OMEGA_URL, timeout=_TIMEOUT_SECS) as response:
            # The Omega response should ONLY be a 0 or 1.  If it's neither, keep
            # the response as None so the caller knows not to do anything with
            # it.
            omega_response = int(response.read())
            if omega_response == 0:
                omega = False
            elif omega_response == 1:
                omega = True
    except:
        # If there's any sort of exception, just let it fly; the omega variable
        # will stay as None.
        logger.exception('Something went wrong fetching the Omega Shift flag!')

    # Now we've got data!  Let's get it parsed!  Make it its own method to keep
    # things tidy and well-organized.
    logger.debug('Fetch complete, parsing now.')
    return _parse_stats(json_data, omega)

def _parse_stats(json_blob, omega: bool) -> VstData:
    """Parses the raw VST results into a VstData object."""
    stats = json_blob.get(_JSON_STATS_CATEGORY)
    year_data = stats.get(_JSON_YEAR_DATA_CAGEGORY)
    game_data = stats.get(_JSON_GAME_DATA_CATEGORY)
    donation_data = stats.get(_JSON_DONATION_DATA_CATEGORY)

    # There isn't much processing we need to do, but there IS something.
    miles_total = 0.0
    try:
        miles_total = float(game_data.get(_JSON_ODOMETER, 0.0))
    except ValueError as e:
        # If the run isn't in progress yet, this will be an empty string, which
        # doesn't parse to float.
        pass
    miles_driven = miles_total - _ODOMETER_OFFSET
    trips_taken = miles_driven // _MILES_TO_VEGAS
    is_going_to_tucson = False
    if trips_taken >= 0 and trips_taken % 2 == 1:
        is_going_to_tucson = True

    start_time_millis = year_data.get(_JSON_RUN_START_TIME, 0) * 1000
    right_now_millis = round(time.time() * 1000)
    hours_bussed = (right_now_millis - start_time_millis) // _MILLIS_PER_HOUR
    minutes_bussed = ((right_now_millis - start_time_millis) % _MILLIS_PER_HOUR) // _MILLIS_PER_MINUTE

    donation_total = float(donation_data.get(_JSON_DONATIONS, 0.0))
    to_next_hour = donation_converter.to_next_hour_from_donation_amount(donation_total)
    total_hours = donation_converter.total_hours_for_donation_amount(donation_total)
    
    is_live = bool(year_data.get(_JSON_IS_LIVE, False)) and start_time_millis <= right_now_millis

    current_shift = None
    if omega:
        current_shift = Shift.OMEGA_SHIFT
    else:
        current_shift = get_current_shift()

    return VstData(time_fetched = right_now_millis,
                   donation_total = donation_total,
                   hours_bussed = hours_bussed,
                   minutes_bussed = minutes_bussed,
                   to_next_hour = to_next_hour,
                   total_hours = total_hours,
                   odometer = miles_total,
                   points = game_data.get(_JSON_POINTS, 0),
                   crashes = game_data.get(_JSON_CRASHES, 0),
                   splats = game_data.get(_JSON_SPLATS, 0),
                   stops = game_data.get(_JSON_STOPS, 0),
                   current_shift = current_shift,
                   start_time_millis = start_time_millis,
                   is_live = is_live,
                   is_omega_shift = omega,
                   is_going_to_tucson = is_going_to_tucson)

