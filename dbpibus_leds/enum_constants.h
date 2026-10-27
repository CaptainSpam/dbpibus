/*!
  @file
    Various helpful enums.
*/

#ifndef ENUM_CONSTANTS_H
#define ENUM_CONSTANTS_H

/** The current driving shift. */
enum class Shift {
  /** Dawn Guard (6a-12n). */
  SHIFT_DAWNGUARD,
  /** Alpha Flight (12n-6p). */
  SHIFT_ALPHAFLIGHT,
  /** Night Watch (6p-12m). */
  SHIFT_NIGHTWATCH,
  /** Zeta Shift (12m-6a). */
  SHIFT_ZETASHIFT,
  /** Omega Shift (whatever's left over). */
  SHIFT_OMEGASHIFT,
  /** Invalid shift, should only happen at boot time. */
  SHIFT_INVALID = -1
};

/**
 * The type of idle animation for the lights.  This is what the cabin lights use
 * in all cases and what the ground effects use if they're set to match the
 * cabin lights.
 */
enum class IdleType {
  /** Lights should be off entirely during idle. */
  IDLE_OFF,
  /** Lights should be on during idle, but shouldn't rotate. */
  IDLE_STATIC,
  /**
   * Lights should be on during idle and should rotate slowly at the end of the
   * cycle.
   */
  IDLE_SLOW,
  /**
  * Lights should be on during idle and should rotate not as slowly at the end
  * of the cycle.
  */
  IDLE_FAST
};

#endif
