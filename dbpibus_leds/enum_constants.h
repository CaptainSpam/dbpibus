/*!
  @file
    Various constants that would be enums in other languages.
*/

const int SHIFT_DAWNGUARD = 0;
const int SHIFT_ALPHAFLIGHT = 1;
const int SHIFT_NIGHTWATCH = 2;
const int SHIFT_ZETASHIFT = 3;
const int SHIFT_OMEGASHIFT = 4;
// This should only happen at boot, before we get a shift.
const int SHIFT_INVALID = -1;

// Lights should be off entirely during idle.
const int IDLE_OFF = 0;
// Lights should be on during idle, but shouldn't rotate.
const int IDLE_STATIC = 1;
// Lights should be on during idle and should rotate slowly at the end of the
// cycle.
const int IDLE_SLOW = 2;
// Lights should be on during idle and should rotate not as slowly at the end
// of the cycle.
const int IDLE_FAST = 3;
