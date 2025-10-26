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
_JSON_ODOMETER = 'Current Mileage'
_JSON_POINTS = 'Points: Total'
_JSON_CRASHES = 'Crashes: Total'
_JSON_SPLATS = 'Bug Splats: Total'
_JSON_STOPS = 'Bus Stops: Total'
_JSON_IS_LIVE = 'Run Live'
_JSON_DONATIONS = 'Total Raised'
_JSON_RUN_START_TIME = 'Year Start UNIX-Time'

_YEAR_OFFSET = 2006
# Floats should be okay here, unless Python has issues with the hundredths digit.
# It might, you never know.
_ODOMETER_OFFSET = 70109.3
_MILES_TO_VEGAS = 360
_MILLIS_PER_MINUTE = 1000 * 60
_MILLIS_PER_HOUR = _MILLIS_PER_MINUTE * 60

def _make_stats_url_for_year(year):
    numbered_run = year - _YEAR_OFFSET
    return f'{_URL_PREFIX}DB{numbered_run}/data/DB{numbered_run}_stats.json'

def get_current_stats() -> VstData:
    """Fetches the current stats from the VST."""
    # First, try for this year.
    year = datetime.now().year
    json_data = None

    try:
        logger.debug(f'Fetching data for {year}...')
        with urllib.request.urlopen(_make_stats_url_for_year(year)) as response:
            json_data = json.loads(response.read())
    except HTTPError as e:
        if e.code == 404:
            # Whoops, it doesn't exist yet.  Back off a year.  If THIS doesn't
            # work, then we throw.
            logger.debug(f'{year} has no data yet, trying again with {year - 1}...')
            with urllib.request.urlopen(_make_stats_url_for_year(year - 1)) as response:
                json_data = json.loads(response.read())

    # Also, check if it's omega or not.
    omega = None
    try:
        logger.debug('Checking if Omega Shift is live...')
        with urllib.request.urlopen(_IS_OMEGA_URL) as response:
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
    return _parse_stats(json_data[0], omega)

def _parse_stats(json_blob, omega: bool) -> VstData:
    """Parses the raw VST results into a VstData object."""
    logger.debug(f'Parsing data blob: {json_blob}')
    # There isn't much processing we need to do, but there IS something.
    miles_total = float(json_blob.get(_JSON_ODOMETER, 0.0))
    miles_driven = miles_total - _ODOMETER_OFFSET
    trips_taken = miles_driven // _MILES_TO_VEGAS
    is_going_to_tucson = False
    if trips_taken >= 0 and trips_taken % 2 == 1:
        is_going_to_tucson = True

    start_time_millis = json_blob.get(_JSON_RUN_START_TIME, 0) * 1000
    right_now_millis = round(time.time() * 1000)
    hours_bussed = (right_now_millis - start_time_millis) // _MILLIS_PER_HOUR
    minutes_bussed = ((right_now_millis - start_time_millis) % _MILLIS_PER_HOUR) // _MILLIS_PER_MINUTE

    donation_total = float(json_blob.get(_JSON_DONATIONS, 0.0))
    to_next_hour = donation_converter.to_next_hour_from_donation_amount(donation_total)
    total_hours = donation_converter.total_hours_for_donation_amount(donation_total)

    current_shift = None
    if omega:
        current_shift = Shift.OMEGA_SHIFT
    else:
        current_shift = get_current_shift()

    return VstData(time_fetched = right_now_millis,
                   donation_total = float(json_blob.get(_JSON_DONATIONS, 0.0)),
                   hours_bussed = hours_bussed,
                   minutes_bussed = minutes_bussed,
                   to_next_hour = to_next_hour,
                   total_hours = total_hours,
                   odometer = miles_total,
                   points = json_blob.get(_JSON_POINTS, 0),
                   crashes = json_blob.get(_JSON_CRASHES, 0),
                   splats = json_blob.get(_JSON_SPLATS, 0),
                   stops = json_blob.get(_JSON_STOPS, 0),
                   current_shift = current_shift,
                   is_live = bool(json_blob.get(_JSON_IS_LIVE, False)),
                   is_omega_shift = omega,
                   is_going_to_tucson = is_going_to_tucson)

