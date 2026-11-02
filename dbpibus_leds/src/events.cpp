/*!
  @file
    Definition of the events functions.
*/

#include "events.h"
#include "globals.h"

bool do_event_animation(EventAnimation event, unsigned long now_millis, unsigned long last_animation_began_millis) {
  if(event == EventAnimation::NONE) {
    // If nothing's being animated, stop right away and return false.
    return false;
  }

  // TODO: Events!
  return false;
}

const AnimationStep ANIMATION_BUS_STOP[] = {
  {1300, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_WHITE, Adafruit_NeoPixel::Color(128, 128, 128)},
  {3000, AnimationType::SOLID_COLOR, Adafruit_NeoPixel::Color(128, 128, 128), COLOR_OFF, COLOR_OFF},
  {1400, AnimationType::WASH_MIDDLE_IN, Adafruit_NeoPixel::Color(128, 128, 128), COLOR_WHITE, COLOR_OFF},
  {0, AnimationType::END, COLOR_OFF, COLOR_OFF, COLOR_OFF}
};

const AnimationStep ANIMATION_CRASH[] = {
  {800, AnimationType::WASH_BACK_FRONT, COLOR_OFF, COLOR_RED, Adafruit_NeoPixel::Color(128, 0, 0)},
  {1200, AnimationType::FADE_COLORS, Adafruit_NeoPixel::Color(128, 0, 0), COLOR_RED, COLOR_OFF},
  {2500, AnimationType::FADE_COLORS, COLOR_RED, COLOR_OFF, COLOR_OFF},
  {500, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {0, AnimationType::END, COLOR_OFF, COLOR_OFF, COLOR_OFF}
};

const AnimationStep ANIMATION_BUG_SPLAT[] = {
  {1000, AnimationType::WASH_BACK_FRONT, COLOR_OFF, COLOR_GREEN, Adafruit_NeoPixel::Color(0, 128, 0)},
  {2300, AnimationType::SOLID_COLOR, Adafruit_NeoPixel::Color(128, 0, 0), COLOR_OFF, COLOR_OFF},
  {2600, AnimationType::FADE_COLORS, Adafruit_NeoPixel::Color(128, 0, 0), COLOR_OFF, COLOR_OFF},
  {0, AnimationType::END, COLOR_OFF, COLOR_OFF, COLOR_OFF}
};

const AnimationStep ANIMATION_OMEGA_SHIFT[] = {
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_DAWNGUARD, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_ALPHAFLIGHT, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_NIGHTWATCH, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_ZETASHIFT, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_DAWNGUARD, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_ALPHAFLIGHT, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_NIGHTWATCH, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_ZETASHIFT, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_DAWNGUARD, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_ALPHAFLIGHT, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_NIGHTWATCH, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {1000, AnimationType::WASH_MIDDLE_OUT, COLOR_OFF, COLOR_WHITE, COLOR_OFF},
  {1000, AnimationType::SOLID_COLOR, COLOR_OFF, COLOR_OFF, COLOR_OFF},
  {0, AnimationType::END, COLOR_OFF, COLOR_OFF, COLOR_OFF}
};
