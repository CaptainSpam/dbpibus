#include <Adafruit_NeoPixel.h>

#include "enum_constants.h"

/*!
  @file
    The various static colors used throughout the light shows.
*/

// A few handy utility colors.
const int COLOR_RED = Adafruit_NeoPixel::Color(255, 0, 0);
const int COLOR_GREEN = Adafruit_NeoPixel::Color(0, 255, 0);
const int COLOR_BLUE = Adafruit_NeoPixel::Color(0, 0, 255);
const int COLOR_MAGENTA = Adafruit_NeoPixel::Color(255, 0, 255);
const int COLOR_YELLOW = Adafruit_NeoPixel::Color(255, 255, 0);
const int COLOR_WHITE = Adafruit_NeoPixel::Color(255, 255, 255);
const int COLOR_OFF = Adafruit_NeoPixel::Color(0, 0, 0);

// The shift-specific colors.  Note, there is no single color for Omega;
// that'll be represented by all four colors.
const int COLOR_DAWNGUARD = Adafruit_NeoPixel::Color(156, 73, 12);
const int COLOR_ALPHAFLIGHT = Adafruit_NeoPixel::Color(105, 3, 9);
const int COLOR_NIGHTWATCH = Adafruit_NeoPixel::Color(8, 82, 135);
const int COLOR_ZETASHIFT = Adafruit_NeoPixel::Color(41, 12, 77);

// The idle color arrays.  These will be repeated along the strand for as many
// times as needed.
const int IDLE_COLORS_ARR_LEN = 4;
const int IDLE_COLORS_DAWNGUARD[] = {COLOR_DAWNGUARD, COLOR_WHITE, COLOR_DAWNGUARD, COLOR_WHITE};
const int IDLE_COLORS_ALPHAFLIGHT[] = {COLOR_ALPHAFLIGHT, COLOR_WHITE, COLOR_ALPHAFLIGHT, COLOR_WHITE};
const int IDLE_COLORS_NIGHTWATCH[] = {COLOR_NIGHTWATCH, COLOR_WHITE, COLOR_NIGHTWATCH, COLOR_WHITE};
const int IDLE_COLORS_ZETASHIFT[] = {COLOR_ZETASHIFT, COLOR_WHITE, COLOR_ZETASHIFT, COLOR_WHITE};
const int IDLE_COLORS_OMEGASHIFT[] = {COLOR_DAWNGUARD, COLOR_ALPHAFLIGHT, COLOR_NIGHTWATCH, COLOR_ZETASHIFT};

/**
 * Returns a new color made from blending the two input colors together by the
 * specified amount.
 *
 * @param color_a the first color
 * @param color_b the second color
 * @param amount the percentage of transition between the first and second
 *               colors (will be clamped to (0.0, 1.0))
 */
int blend_colors(int color_a, int color_b, float amount);

/**
 * Puts the colors colors of the given shift in the given array of the given
 * size.
 *
 * @param shift the constant of the driving shift
 * @param arr an array into which the shift colors will be written
 * @param size the size of the array
 */
void get_shift_colors(Shift shift, int *arr, int size);
