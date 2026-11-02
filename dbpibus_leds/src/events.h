/*!
  @file
    Header for the events functions.
*/

#ifndef EVENTS_H
#define EVENTS_H

#include <Adafruit_NeoPixel.h>

#include "enum_constants.h"
#include "colors.h"

/** The types of animations available. */
enum class AnimationType {
  /**
   * Wash from one color to another, with the wash starting at the front of the
   * bus and moving backward.
   * 
   * color1: Starting color for all LEDs.
   * color2: Color of the wash point.
   * color3: Ending color for all LEDs (after wash passes over them).
   */
  WASH_FRONT_BACK,
  /**
   * Wash from one color to another, with the wash starting at the back of the
   * bus and moving forward.
   * 
   * color1: Starting color for all LEDs.
   * color2: Color of the wash point.
   * color3: Ending color for all LEDs (after wash passes over them).
   */
  WASH_BACK_FRONT,
  /**
   * Wash from one color to another, with the wash starting at the middle of the
   * bus and moving out to the front and back.
   * 
   * color1: Starting color for all LEDs.
   * color2: Color of the wash point.
   * color3: Ending color for all LEDs (after wash passes over them).
   */
  WASH_MIDDLE_OUT,
  /**
   * Wash from one color to another, with the wash starting at both ends of the
   * bus and moving inward to the middle.
   * 
   * color1: Starting color for all LEDs.
   * color2: Color of the wash point.
   * color3: Ending color for all LEDs (after wash passes over them).
   */
  WASH_MIDDLE_IN,
  /**
   * Hold a single color for all LEDs.
   * 
   * color1: Color to hold.
   * color2: Ignored.
   * color3: Ignored.
   */
  SOLID_COLOR,
  /**
   * Fade from one color to another.
   *
   * color1: Starting color.
   * color2: Ending color.
   * color3: Ignored.
   */
  FADE_COLORS,
  /**
   * Sentinel value that marks the end of the animation.  This MUST be at the
   * end of each animation, else things will go bad in a "shoot off into memory"
   * sort of way.  Once this is hit, the animation ends immediately and the
   * light show returns to idle.
   *
   * color1: Ignored.
   * color2: Ignored.
   * color3: Ignored.
   */
  END,
};

class AnimationEvent {
  /**
   * Does whatever is needed for the given amount of elapsed time.  The elapsed
   * time, in this case, refers to the time since this event began, not since
   * the overall animation began.
   *
   * @param strip the NeoPixel strip object
   * @param elapsed_time_millis the time since this event began, in millis
   * @return true if this event has more to go, false if it's finished and the caller should advance to the next one
   */
  virtual bool do_frame(Adafruit_NeoPixel strip, unsigned long elapsed_time_millis) = 0;

  /** Whether or not this is the end-step AnimationEvent. */
  virtual bool is_end() {
    return false;
  }
};

/** Sentinel event class that indicates this is the end of the animation. */
class EndEvent : AnimationEvent {
  bool do_frame(Adafruit_NeoPixel strip, unsigned long elapsed_time_millis) override {
    return false;
  }

  bool is_end() override {
    return true;
  }
};

/** A single step in an animation sequence. */
struct AnimationStep {
  unsigned int duration_millis;
  AnimationType type;
  uint32_t color1;
  uint32_t color2;
  uint32_t color3;
};

/**
 * Do whatever is needed for the next frame of the current event animation.
 * This will return true if any animation occurred (and thus the idle lights
 * should be ignored), and false if the current event animation has ended (and
 * thus the idle lights should be processed).
 *
 * @param event the EventAnimation to run
 * @param now_millis the current time, in millis
 * @param last_animation_began_millis when the most recent animation began, in millis
 * @return true if an event was handled at all, false if not
 */
bool do_event_animation(EventAnimation event, unsigned long now_millis, unsigned long last_animation_began_millis);

#endif
