/*!
  @file
    Various constants for things directly used as values.
*/

// Time it takes for a single cycle of the idle animation lights.  The lights
// will remain at steady colors for this long minus the rotation times below,
// depending on user settings.  Obviously, they won't rotate at all if the
// user's either turned the lights off or has them in static mode.
const int IDLE_CYCLE_TIME_MILLIS = 60000;
// Time the idle animations take to rotate the lights in slow fade mode.
const int IDLE_ROTATE_SLOW_TIME_MILLIS = 5000;
// Time the idle animations take to rotate the lights in fast fade mode.
const int IDLE_ROTATE_FAST_TIME_MILLIS = 1000;
