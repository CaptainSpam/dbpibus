/*!
  @file
    Header for the idle animation functions.
*/

#ifndef IDLE_H
#define IDLE_H

#include <cstdint>

#include "enum_constants.h"

/**
 * Do whatever is necessary for the idle animation.
 *
 * @param now_millis the current time, in millis
 * @param shift the current driving shift
 * @param idle_type the type of idle animation
 * @param ground_effects the type of ground effects
 */
void do_idle_animation(unsigned long now_millis, Shift shift, IdleType idle_type, GroundEffects ground_effects);

void do_cabin_lights(unsigned long now_millis, IdleType idle_type, Shift shift);
void do_ground_effects(unsigned long now_millis, GroundEffects ground_effects, IdleType idle_type, Shift shift);
void do_clock_lights(int pos1, int gap, const uint32_t *shift_colors, int shift_colors_size);
void do_blended_lights(int start, int end, unsigned long now_millis, IdleType idle_type, const uint32_t *colors, int color_size);

#endif
