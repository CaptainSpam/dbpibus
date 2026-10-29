/*!
  @file
    Header for the events functions.
*/

#ifndef EVENTS_H
#define EVENTS_H

#include "enum_constants.h"

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
