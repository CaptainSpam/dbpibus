/*!
  @file
    Header for the idle animation functions.
*/

#ifndef IDLE_H
#define IDLE_H

#include "enum_constants.h"

/**
 * Do whatever is necessary for the idle animation.
 *
 * @param now_millis the current time, in millis
 */
void do_idle_animation(unsigned long now_millis);

void do_cabin_lights(unsigned long now_millis, IdleType idle_type, Shift shift);
void do_ground_effects(unsigned long now_millis, GroundEffects ground_effects, IdleType idle_type, Shift shift);
void do_clock_lights(int pos1, int gap, const int *shift_colors, int shift_colors_size);
void do_blended_lights(int start, int end, unsigned long now_millis, const int *colors, int color_size);

#endif
