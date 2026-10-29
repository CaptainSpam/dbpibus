/*!
  @file
    Global stuff.
*/

#ifndef GLOBALS_H
#define GLOBALS_H

#include <Adafruit_NeoPixel.h>

/** The Pico pin the NeoPixel strand is using for data. */
const int NEOPIXEL_PIN = 16;
/** The number of lights in the NeoPixel strand.  Change as necessary. */
const int NEOPIXEL_STRAND_LENGTH = 20;
/** The NeoPixel strip object. */
Adafruit_NeoPixel strip(NEOPIXEL_STRAND_LENGTH, NEOPIXEL_PIN);

/**
 * Number of lights in the cabin of the bus.  Anything past this is assumed to
 * be ground effect lights.  Also change as necessary.
 */
const int CABIN_LIGHT_COUNT = 12;
/** The number of ground effect lights, for convenience. */
const int GROUND_EFFECTS_LIGHT_COUNT = NEOPIXEL_STRAND_LENGTH - CABIN_LIGHT_COUNT;

#endif
