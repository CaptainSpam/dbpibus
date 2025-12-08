#include <Adafruit_NeoPixel.h>

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

// We'll use the "canon" shift colors for now, as I think NeoPixels are a bit
// better at making clean colors than the LCD backlight.  These will probably
// be tweaked.  Note, there is no single color for Omega; that'll be represented
// by all four colors.
const int COLOR_DAWNGUARD = Adafruit_NeoPixel::Color(237, 128, 49);
const int COLOR_ALPHAFLIGHT = Adafruit_NeoPixel::Color(176, 34, 42);
const int COLOR_NIGHTWATCH = Adafruit_NeoPixel::Color(21, 115, 182);
const int COLOR_ZETASHIFT = Adafruit_NeoPixel::Color(95, 57, 134);

// The idle color arrays.  These will be repeated along the strand for as many
// times as needed.
const int IDLE_COLORS_DAWNGUARD[] = {COLOR_DAWNGUARD, COLOR_WHITE};
const int IDLE_COLORS_ALPHAFLIGHT[] = {COLOR_ALPHAFLIGHT, COLOR_WHITE};
const int IDLE_COLORS_NIGHTWATCH[] = {COLOR_NIGHTWATCH, COLOR_WHITE};
const int IDLE_COLORS_ZETASHIFT[] = {COLOR_ZETASHIFT, COLOR_WHITE};
const int IDLE_COLORS_OMEGASHIFT[] = {COLOR_DAWNGUARD, COLOR_ALPHAFLIGHT, COLOR_NIGHTWATCH, COLOR_ZETASHIFT};