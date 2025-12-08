/*!
  @file
    Various useful serial communication constants.
*/

// Start an event animation (point, crash, bus stop, etc).
const char COMMAND_EVENT_ANIMATION = 'E';
// Stop an active event animation and return to idle.
const char COMMAND_STOP_EVENT = 'X';
// Set the current idle animation (shift colors, basically).
const char COMMAND_SET_IDLE_ANIMATION = 'I';
// Updates a config setting relevant to the lights.
const char COMMAND_UPDATE_CONFIG = 'U';

// Config setting for the idle type.
const char CONFIG_IDLE_TYPE = 't';

// Lights should be off during idle.
const char IDLE_TYPE_OFF = '0';
// Lights don't animate during idle.
const char IDLE_TYPE_STATIC = '1';
// Lights slowly fade and rotate around during idle.
const char IDLE_TYPE_SLOW = '2';
// Lights more quickly fade and rotate around during idle.
const char IDLE_TYPE_FAST = '3';

// The orange of Dawn Guard.
const char IDLE_ANIMATION_DAWNGUARD = '0';
// The red of Alpha Flight.
const char IDLE_ANIMATION_ALPHAFLIGHT = '1';
// The blue of Night Watch.
const char IDLE_ANIMATION_NIGHTWATCH = '2';
// The purple of Zeta Shift.
const char IDLE_ANIMATION_ZETASHIFT = '3';
// All four shift colors for Omega Shift.
const char IDLE_ANIMATION_OMEGASHIFT = '4';

// POINT GET!
const char EVENT_ANIMATION_POINT = '0';
// CRASH!
const char EVENT_ANIMATION_CRASH = '1';
// Bus stop!
const char EVENT_ANIMATION_BUS_STOP = '2';
// Bug splat!
const char EVENT_ANIMATION_BUG_SPLAT = '3';