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