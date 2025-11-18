#!/usr/bin/env python3

"""Various config-handling stuff."""

import os
import json
import copy
from enum import StrEnum

_CONFIG_FILE = f"{os.path.expanduser('~')}/dbpibus.json"

class ConfigKey(StrEnum):
    """Configuration keys."""
    # If/when shift transition animations are shown.
    SHOW_SHIFT_ANIM = 'ShowShiftAnim'
    # If/when event animations are shown.
    SHOW_EVENT_ANIM = 'ShowEventAnim'
    # LCD backlight color (as an enum; use shift_data.py to resolve to a color).
    LCD_COLOR = 'LcdColor'
    # If/when the current time page should be shown during a run.
    SHOW_TIME_IN_RUN = 'ShowTimeInRun'
    # If/when the current time page should be shown during the preseason.
    SHOW_TIME_IN_PRESEASON = 'ShowTimeInPreseason'
    # If/when the current time page should be shown during the offseason.
    SHOW_TIME_IN_OFFSEASON = 'ShowTimeInOffseason'
    # Format of the time, if displayed.
    TIME_FORMAT = 'TimeFormat'
    # Format of the date, if displayed.
    DATE_FORMAT = 'DateFormat'
    # Format of points and crashes.
    POINTS_CRASHES = 'PointsCrashes'

class ShiftAnim(StrEnum):
    """Options for SHOW_SHIFT_ANIM."""
    # Always show shift transitions.
    ALWAYS = 'Always'
    # Only show shift transisions during a DBfH run.
    ONLY_IN_SEASON = 'OnlyInSeason'
    # Never show shift transisions.
    NEVER = 'Never'

class EventAnim(StrEnum):
    """Options for SHOW_EVENT_ANIM."""
    # Always show event animations.
    ALWAYS = 'Always'
    # Never show event animations.
    NEVER = 'Never'

class LcdColor(StrEnum):
    """Options for LCD_COLOR."""
    # Use whatever color matches the current shift.
    CURRENT_SHIFT = 'CurrentShift'
    # Always use Dawn Guard's color (orange).
    DAWN_GUARD = 'DawnGuard'
    # Always use Alpha Flight's color (red).
    ALPHA_FLIGHT = 'AlphaFlight'
    # Always use Night Watch's color (blue).
    NIGHT_WATCH = 'NightWatch'
    # Always use Zeta Shift's color (purple).
    ZETA_SHIFT = 'ZetaShift'
    # Always use Omega Shift's color (grey/white).
    OMEGA_SHIFT = 'OmegaShift'

class ShowTime(StrEnum):
    """Options for showing the time.  It's a boolean, yes, but it's more
    consistent to make it an enum."""
    YES = 'Yes'
    NO = 'No'

class TimeFormat(StrEnum):
    """Time format."""
    TWELVE_HOUR = '12Hour'
    TWENTY_FOUR_HOUR = '24Hour'

class DateFormat(StrEnum):
    """Date format.  No judgements allowed."""
    YYYYMMDD = 'YYYYMMDD'
    DDMMYYYY = 'DDMMYYYY'
    MMDDYYYY = 'MMDDYYYY'

class PointsCrashes(StrEnum):
    """How to format points and crashes."""
    # As two separate pages.
    SEPARATE = 'Separate'
    # As one PT:CR page.
    PTCR = 'PTCR'

def _make_default_config():
    """Makes a new default config dict."""
    return {
        ConfigKey.SHOW_SHIFT_ANIM: ShiftAnim.ALWAYS,
        ConfigKey.SHOW_EVENT_ANIM: EventAnim.ALWAYS,
        ConfigKey.LCD_COLOR: LcdColor.CURRENT_SHIFT,
        ConfigKey.SHOW_TIME_IN_RUN: ShowTime.NO,
        ConfigKey.SHOW_TIME_IN_PRESEASON: ShowTime.NO,
        ConfigKey.SHOW_TIME_IN_OFFSEASON: ShowTime.NO,
        ConfigKey.TIME_FORMAT: TimeFormat.TWELVE_HOUR,
        ConfigKey.DATE_FORMAT: DateFormat.YYYYMMDD,
        ConfigKey.POINTS_CRASHES: PointsCrashes.SEPARATE,
    }

_current_config = None

def _validate(key: ConfigKey, value: any) -> bool:
    """Validates that the given value is valid for the given key.  Returns True
    if valid, False if not."""
    try:
        _validate_or_raise(key, value)
        return True
    except:
        return False

def _validate_or_raise(key: ConfigKey, value: any):
    """Validates that the given value is valid for the given key.  Raises an
    exception if validation fails."""
    match key:
        case ConfigKey.SHOW_SHIFT_ANIM:
            ShiftAnim(value)
        case ConfigKey.SHOW_EVENT_ANIM:
            EventAnim(value)
        case ConfigKey.LCD_COLOR:
            LcdColor(value)
        case ConfigKey.SHOW_TIME_IN_RUN:
            ShowTime(value)
        case ConfigKey.SHOW_TIME_IN_PRESEASON:
            ShowTime(value)
        case ConfigKey.SHOW_TIME_IN_OFFSEASON:
            ShowTime(value)
        case ConfigKey.TIME_FORMAT:
            TimeFormat(value)
        case ConfigKey.DATE_FORMAT:
            DateFormat(value)
        case ConfigKey.POINTS_CRASHES:
            PointsCrashes(value)
        case _:
            raise ValueError(f'Invalid key {key}')

def load_config():
    """Loads config from disk.  Raises an exception if what's on disk isn't
    valid JSON or can't be opened (but not if it doesn't exist).  Doesn't
    actually return anything; this populates the stored config so that things
    like get_setting() and set_setting() work.

    If it IS valid JSON but some values are missing or invalid, the loaded
    settings will be reset to their defaults.  The next time settings are
    written (i.e. the next set_setting() call), anything invalid will be
    clobbered.

    If the loaded JSON has more data than what we know about, these will be
    preserved, though whether or not that does you any good depends on just what
    you were doing with making new settings without adding them to the whole
    structure here in the first place.  This is supposed to be an embedded
    thingamajig, after all."""
    global _current_config
    global _CONFIG_FILE
    
    try:
        with open(_CONFIG_FILE) as json_file:
            new_config = _make_default_config()
            pristine_defaults = _make_default_config()

            json_data = json.load(json_file)
            new_config.update(json_data)

            # Now, validate what we've got.  Check each of the enum values to
            # see if they raise exceptions, and pull them back to their defaults
            # if they do.
            # TODO: If we wind up with more settings, we probably want to do
            # this less bluntly.
            if not _validate(ConfigKey.SHOW_SHIFT_ANIM, new_config[ConfigKey.SHOW_SHIFT_ANIM]):
                new_config[ConfigKey.SHOW_SHIFT_ANIM] = pristine_defaults[ConfigKey.SHOW_SHIFT_ANIM]

            if not _validate(ConfigKey.SHOW_EVENT_ANIM, new_config[ConfigKey.SHOW_EVENT_ANIM]):
                new_config[ConfigKey.SHOW_EVENT_ANIM] = pristine_defaults[ConfigKey.SHOW_EVENT_ANIM]

            if not _validate(ConfigKey.LCD_COLOR, new_config[ConfigKey.LCD_COLOR]):
                new_config[ConfigKey.LCD_COLOR] = pristine_defaults[ConfigKey.LCD_COLOR]

            if not _validate(ConfigKey.SHOW_TIME_IN_RUN, new_config[ConfigKey.SHOW_TIME_IN_RUN]):
                new_config[ConfigKey.SHOW_TIME_IN_RUN] = pristine_defaults[ConfigKey.SHOW_TIME_IN_RUN]

            if not _validate(ConfigKey.SHOW_TIME_IN_PRESEASON, new_config[ConfigKey.SHOW_TIME_IN_PRESEASON]):
                new_config[ConfigKey.SHOW_TIME_IN_PRESEASON] = pristine_defaults[ConfigKey.SHOW_TIME_IN_PRESEASON]

            if not _validate(ConfigKey.SHOW_TIME_IN_OFFSEASON, new_config[ConfigKey.SHOW_TIME_IN_OFFSEASON]):
                new_config[ConfigKey.SHOW_TIME_IN_OFFSEASON] = pristine_defaults[ConfigKey.SHOW_TIME_IN_OFFSEASON]

            if not _validate(ConfigKey.TIME_FORMAT, new_config[ConfigKey.TIME_FORMAT]):
                new_config[ConfigKey.TIME_FORMAT] = pristine_defaults[ConfigKey.TIME_FORMAT]

            if not _validate(ConfigKey.DATE_FORMAT, new_config[ConfigKey.DATE_FORMAT]):
                new_config[ConfigKey.DATE_FORMAT] = pristine_defaults[ConfigKey.DATE_FORMAT]

            if not _validate(ConfigKey.POINTS_CRASHES, new_config[ConfigKey.POINTS_CRASHES]):
                new_config[ConfigKey.POINTS_CRASHES] = pristine_defaults[ConfigKey.POINTS_CRASHES]

            # That's it!  Stash this away as our "real" version.
            _current_config = new_config
    except FileNotFoundError as e:
        # Whoops, the file doesn't exist.  Just copy the default in.
        _current_config = _make_default_config()
        return

def save_config():
    """Writes the current config out to the file.  Will raise an exception if it
    can't do so.

    This is generally intended to be called internally after each set_setting()
    call, but if you've got some reason to ensure the config file is written,
    feel free."""
    global _current_config
    global _CONFIG_FILE

    with open(_CONFIG_FILE, 'w') as json_file:
        json.dump(_current_config, json_file)
    os.sync()

def set_setting(key: ConfigKey, value: StrEnum):
    """Sets a setting key to the given value, then saves the config back to
    disk.  Raises an exception if something's amiss."""
    global _current_config

    _validate_or_raise(key, value)
    _current_config[key] = value
    save_config()

def get_setting(key: ConfigKey) -> any:
    """Gets a setting from the current config.  Raises an exception if the key
    doesn't exist."""
    global _current_config

    return _current_config[key]
