/*!
  @file
    Various constants for things directly used as values.
*/

#ifndef VALUE_CONSTANTS_H
#define VALUE_CONSTANTS_H

// Time it takes for a single cycle of the idle animation lights.  The lights
// will remain at steady colors for this long minus the rotation times below,
// depending on user settings.  Obviously, they won't rotate at all if the
// user's either turned the lights off or has them in static mode.
const int IDLE_CYCLE_TIME_MILLIS = 60000;
// Time the idle animations take to rotate the lights in slow fade mode.
const int IDLE_ROTATE_SLOW_TIME_MILLIS = 5000;
// Time the idle animations take to rotate the lights in fast fade mode.
const int IDLE_ROTATE_FAST_TIME_MILLIS = 1000;

// Time a single pulse cycle takes.
const int PULSE_CYCLE_TIME_MILLIS = 3000;
// Time a pulse holds at full brightness before starting a new cycle.
const int PULSE_HOLD_TIME_MILLIS = 10000;

#endif
