/*!
  @file
    Various helpful enums.
*/

#ifndef ENUM_CONSTANTS_H
#define ENUM_CONSTANTS_H

/** The current driving shift. */
enum class Shift {
  /** Dawn Guard (6a-12n). */
  DAWNGUARD,
  /** Alpha Flight (12n-6p). */
  ALPHAFLIGHT,
  /** Night Watch (6p-12m). */
  NIGHTWATCH,
  /** Zeta Shift (12m-6a). */
  ZETASHIFT,
  /** Omega Shift (whatever's left over). */
  OMEGASHIFT,
  /** Invalid shift, should only happen at boot time. */
  INVALID = -1
};

/**
 * The type of idle animation for the lights.  This is what the cabin lights use
 * in all cases and what the ground effects use if they're set to match the
 * cabin lights.
 */
enum class IdleType {
  /** Lights should be off entirely during idle. */
  OFF,
  /** Lights should be on during idle, but shouldn't rotate. */
  STATIC,
  /**
   * Lights should be on during idle and should rotate slowly at the end of the
   * cycle.
   */
  SLOW,
  /**
  * Lights should be on during idle and should rotate not as slowly at the end
  * of the cycle.
  */
  FAST
};

/** The type of ground effects to use. */
enum class GroundEffects {
  /** Ground effect lights are off. */
  OFF,
  /** Ground effects match the idle settings. */
  MATCH_IDLE,
  /** Use a slow pulsating effect for ground effects. */
  PULSE,
  /** Use clock-like chase lights for ground effects. */
  CLOCK
};

/** Event animations.  Also includes shift transitions. */
enum class EventAnimation {
  /** Point get! */
  POINT,
  /** CRASH! */
  CRASH,
  /** Bus stop! */
  BUS_STOP,
  /** Bug splat! */
  BUG_SPLAT,
  /** Dawn Guard transition. */
  DAWN_GUARD,
  /** Alpha Flight transition. */
  ALPHA_FLIGHT,
  /** Night Watch transition. */
  NIGHT_WATCH,
  /** Zeta Shift transition. */
  ZETA_SHIFT,
  /** Omega Shift transition. */
  OMEGA_SHIFT
};

#endif
