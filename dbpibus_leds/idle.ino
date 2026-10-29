/*!
  @file
    Definitions of the idle animation functions.
*/

#include "globals.h"
#include "enum_constants.h"
#include "value_constants.h"
#include "colors.h"

void do_idle_animation(unsigned long now_millis) {
  do_cabin_lights(now_millis, idle_type, current_idle);
  do_ground_effects(now_millis, ground_effects, idle_type, current_idle);

  // Apply whatever just happened.
  strip.show();
}

void do_cabin_lights(unsigned long now_millis, IdleType idle_type, Shift shift) {
  if(shift == Shift::INVALID) {
    // If we don't have shift data yet, ignore it.  This will keep it in rainbow
    // mode until the first update hits, which will be a pretty good indicator
    // that data hasn't arrived.
    return;
  }

  if(idle_type == IdleType::OFF) {
    // Idle's off, so turn off all the lights and ignore the rest of the
    // function.
    strip.fill(COLOR_OFF, 0, CABIN_LIGHT_COUNT);
    return;
  }

  int shift_colors[IDLE_COLORS_ARR_LEN];
  get_shift_colors(shift, shift_colors, IDLE_COLORS_ARR_LEN);

  if(idle_type == IdleType::STATIC) {
    // Idle's static, so just fill it with the necessary colors.
    for(int i = 0; i < CABIN_LIGHT_COUNT; i++) {
      strip.setPixelColor(i, shift_colors[i % IDLE_COLORS_ARR_LEN]);
    }
    return;
  }

  if(idle_type == IdleType::FAST || idle_type == IdleType::SLOW) {
    do_blended_lights(0, CABIN_LIGHT_COUNT - 1, now_millis, shift_colors, 4);
  }
}

void do_ground_effects(unsigned long now_millis, GroundEffects ground_effects, IdleType idle_type, Shift shift) {
  if(shift == Shift::INVALID) {
    // If we don't have shift data yet, ignore it, just like in idle.
    return;
  }

  if(ground_effects == GroundEffects::OFF) {
    // Turn 'em off.
    strip.fill(COLOR_OFF, CABIN_LIGHT_COUNT, GROUND_EFFECTS_LIGHT_COUNT);
    return;
  }

  int shift_colors[IDLE_COLORS_ARR_LEN];
  get_shift_colors(shift, shift_colors, IDLE_COLORS_ARR_LEN);

  if(ground_effects == GroundEffects::MATCH_IDLE) {
    // In MATCH_IDLE mode, we basically repeat most of the logic for idle.
    if(idle_type == IdleType::OFF) {
      // Idle's off, so turn off the ground lights.
      strip.fill(COLOR_OFF, CABIN_LIGHT_COUNT, GROUND_EFFECTS_LIGHT_COUNT);
      return;
    }

    if(idle_type == IdleType::STATIC) {
      // Idle's static, so just fill it with the necessary colors.
      for(int i = CABIN_LIGHT_COUNT; i < NEOPIXEL_STRAND_LENGTH; i++) {
        strip.setPixelColor(i, shift_colors[i % IDLE_COLORS_ARR_LEN]);
      }
      return;
    }

    if(idle_type == IdleType::FAST || idle_type == IdleType::SLOW) {
      do_blended_lights(CABIN_LIGHT_COUNT, NEOPIXEL_STRAND_LENGTH - 1, now_millis, shift_colors, 4);
    }
  }

  if(ground_effects == GroundEffects::CLOCK) {
    // Tick-tock, Mister P. Jangles.  The number of lights in the chase should
    // scale with the number of ground effect lights available.  First, clear
    // everything.
    strip.fill(COLOR_OFF, CABIN_LIGHT_COUNT, GROUND_EFFECTS_LIGHT_COUNT);

    // We want a tick every second.  Fortunately, that's easy.
    int pos1 = (now_millis / 1000) % GROUND_EFFECTS_LIGHT_COUNT;

    if(GROUND_EFFECTS_LIGHT_COUNT < 8) {
      // Anything less than 8 (or prime), just a single light.
      strip.setPixelColor(CABIN_LIGHT_COUNT + pos1, shift_colors[pos1 % IDLE_COLORS_ARR_LEN]);
    } else if(GROUND_EFFECTS_LIGHT_COUNT % 5 == 0) {
      // If divisble by five, space them out by five spaces.
      do_clock_lights(pos1, 5, shift_colors, IDLE_COLORS_ARR_LEN);
    } else if(GROUND_EFFECTS_LIGHT_COUNT % 4 == 0) {
      // For four, similar.
      do_clock_lights(pos1, 4, shift_colors, IDLE_COLORS_ARR_LEN);
    } else if(GROUND_EFFECTS_LIGHT_COUNT % 3 == 0) {
      // Or three.
      do_clock_lights(pos1, 3, shift_colors, IDLE_COLORS_ARR_LEN);
    } else {
      // If it's not divisible by 5, 4, or 3, assume it's a single.  I'm sure
      // there's a more fanciful algorithm I can use to find an aesthetically
      // pleasing divisor to use here, but I really don't expect there to be
      // more than 12 ground effect lights in the first place.
      strip.setPixelColor(CABIN_LIGHT_COUNT + pos1, shift_colors[pos1 % IDLE_COLORS_ARR_LEN]);
    }
  }

  if(ground_effects == GroundEffects::PULSE) {
    // A pulsating light.  I think we can do this without globals!
    int timing_millis = now_millis % (PULSE_CYCLE_TIME_MILLIS + PULSE_HOLD_TIME_MILLIS);

    if(timing_millis >= PULSE_CYCLE_TIME_MILLIS) {
      // We're past pulse time, hold steady with shift colors.
      for(int i = CABIN_LIGHT_COUNT; i < NEOPIXEL_STRAND_LENGTH; i++) {
        strip.setPixelColor(i, shift_colors[i % IDLE_COLORS_ARR_LEN]);
      }
    } else {
      // We're somewhere in the middle of a pulse!
      float amount = sin((timing_millis / (float)PULSE_CYCLE_TIME_MILLIS) * M_PI);

      for(int i = CABIN_LIGHT_COUNT; i < NEOPIXEL_STRAND_LENGTH; i++) {
        strip.setPixelColor(i, blend_colors(shift_colors[i % IDLE_COLORS_ARR_LEN], COLOR_OFF, amount));
      }
    }
  }
}

void do_clock_lights(int pos1, int gap, const int *shift_colors, int shift_colors_size) {
  // TODO: Make this less global-variable-dependent?
  strip.setPixelColor(CABIN_LIGHT_COUNT + pos1, shift_colors[pos1 % shift_colors_size]);

  int pos_cur = pos1;
  do {
    pos_cur = (pos_cur + gap) % GROUND_EFFECTS_LIGHT_COUNT;
    strip.setPixelColor(CABIN_LIGHT_COUNT + pos_cur, shift_colors[pos_cur % shift_colors_size]);
  } while(pos_cur != pos1);
}

void do_blended_lights(int start, int end, unsigned long now_millis, const int *colors, int color_size) {
  // Determine how long one single cycle takes.
  int fade_time_millis = IDLE_ROTATE_SLOW_TIME_MILLIS;
  if(idle_type == IdleType::FAST) fade_time_millis = IDLE_ROTATE_FAST_TIME_MILLIS;
  int one_cycle_time_millis = IDLE_CYCLE_TIME_MILLIS + fade_time_millis;

  // Where are we in that cycle?
  int time_in_cycle_millis = now_millis % one_cycle_time_millis;

  // There's exactly color_size cycles before the configuration repeats.  Where
  // are we in THAT cycle?
  int cycle_count = (now_millis / one_cycle_time_millis) % color_size;

  if(time_in_cycle_millis < IDLE_CYCLE_TIME_MILLIS) {
    // We're in the static part of the cycle.
    for(int i = start; i <= end; i++) {
      strip.setPixelColor(i, colors[(i + cycle_count) % color_size]);
    }
  } else {
    // Calculate the percent of time that's passed since this fade began and how
    // long it should last.  This WILL likely wind up being over 1.0 eventually;
    // this is okay, as that'll hit the clamp.
    float amount =  1.0 - ((fade_time_millis - (time_in_cycle_millis - IDLE_CYCLE_TIME_MILLIS)) / (float)fade_time_millis);

    // Then, build up a new array of blended colors.
    int faded_colors[4] = {
      blend_colors(colors[0], colors[1], amount),
      blend_colors(colors[1], colors[2], amount),
      blend_colors(colors[2], colors[3], amount),
      blend_colors(colors[3], colors[0], amount)
    };

    // NOW we can display them!
    for(int i = start; i <= end; i++) {
      strip.setPixelColor(i, faded_colors[(i + cycle_count) % IDLE_COLORS_ARR_LEN]);
    }
  }
}