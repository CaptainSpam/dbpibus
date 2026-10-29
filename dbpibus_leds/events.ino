/*!
  @file
    Definition of the events functions.
*/

#include "events.h"
#include "globals.h"

bool do_event_animation(EventAnimation event, unsigned long now_millis, unsigned long last_animation_began_millis) {
  if(event == EventAnimation::INVALID) {
    // This should only come up before any event's been sent from the Zero.
    return false;
  }

  // TODO: Events!
  return false;
}