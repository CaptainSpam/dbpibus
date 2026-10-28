#include <Adafruit_NeoPixel.h>
#include "colors.h"
#include "serial_constants.h"
#include "enum_constants.h"
#include "value_constants.h"

const int NEOPIXEL_PIN = 16;
const int NEOPIXEL_STRAND_LENGTH = 20;
Adafruit_NeoPixel strip(NEOPIXEL_STRAND_LENGTH, NEOPIXEL_PIN);

// Number of lights in the cabin of the bus.  Anything past this is assumed to
// be ground effect lights.
const int CABIN_LIGHT_COUNT = 12;
const int GROUND_EFFECTS_LIGHT_COUNT = NEOPIXEL_STRAND_LENGTH - CABIN_LIGHT_COUNT;

int last_light = -1;
bool showing_lights = true;

Shift current_idle = Shift::INVALID;
IdleType idle_type = IdleType::SLOW;
GroundEffects ground_effects = GroundEffects::MATCH_IDLE;

char current_command = ' ';
char current_config = ' ';

void setup() {
  // TODO: Remove the serial monitor?
  Serial.begin(9600);

  // Fire up some serial!
  Serial1.begin(9600);

  // NeoPixels start up now, too!
  strip.begin();
  // The rainbow is just to confirm I'm sending LED data correctly; this should
  // get overwritten as soon as the Zero boots up and sends data.
  strip.rainbow(0, 3);
  strip.setBrightness(50);
  strip.show();

  // Then, ask for the config to be re-sent, if the Zero's awake at this point.
  // Realistically, the only way it won't is if this is a dev situation, as the
  // it absolutely won't finish booting before the Pico starts running.
  request_config();
}

void loop() {
  // Update all serial data as need be.
  read_serial();

  // Update the lights for the idle version.
  // TODO: Events take priority, so if there's one waiting, this should wait its
  // turn.
  do_idle_animation();
}

void request_config() {
  Serial1.write(REQUEST_CONFIG);
}

// These serial functions are for abstraction purposes.  Y'know, in case I have
// the bright idea to change what pins (or USB) I'm using for serial again.
char get_serial_char() {
  return (char)Serial1.read();
}

bool serial_available() {
  return Serial1.available() > 0;
}

void read_serial() {
  while(serial_available()) {
    // We got something!  It'll be a single character command.  Further data
    // will be dependent on the command.
    char input = get_serial_char();

    // We handle exactly one char at a time, then return.  The program runs too
    // fast for the baud rate, so the next char (for parameters to a command)
    // won't be here in time if we try to handle them all at once.  Thus, we
    // stash the current chars we're processing, resetting once we've processed
    // a full command (or we hit an invalid character).  What I'm saying is this
    // is becoming an ersatz state machine.

    // To that end, are we already in a command?  If not, this may be a command.
    if(current_command == ' ') {
      // But is it a VALID command?  If so, store it and await the next char.
      // If not, ignore it entirely.
      switch(input) {
        case COMMAND_EVENT_ANIMATION:
        case COMMAND_STOP_EVENT:
        case COMMAND_SET_IDLE_ANIMATION:
        case COMMAND_UPDATE_CONFIG:
          current_command = input;
          break;
      }

      return;
    }

    // We ARE in a command!  Well, this has to be an argument FOR that command!
    switch(current_command) {
      case COMMAND_SET_IDLE_ANIMATION: {
        switch(input) {
          case IDLE_ANIMATION_DAWNGUARD:
            current_idle = Shift::DAWNGUARD;
            break;
          case IDLE_ANIMATION_ALPHAFLIGHT:
            current_idle = Shift::ALPHAFLIGHT;
            break;
          case IDLE_ANIMATION_NIGHTWATCH:
            current_idle = Shift::NIGHTWATCH;
            break;
          case IDLE_ANIMATION_ZETASHIFT:
            current_idle = Shift::ZETASHIFT;
            break;
          case IDLE_ANIMATION_OMEGASHIFT:
            current_idle = Shift::OMEGASHIFT;
            break;
        }

        // Valid or not, reset.
        reset_inputs();
        break;
      }
      case COMMAND_UPDATE_CONFIG: {
        if(current_config == ' ') {
          // This should be the option being changed.
          switch(input) {
            case CONFIG_IDLE_TYPE:
            case CONFIG_GROUND_EFFECTS:
              current_config = input;
              break;
            default:
              // Invalid!
              reset_inputs();
          }

          // Either way, wait for the next input.
          return;
        }

        // So THIS input should be the specific option for the given config.
        switch(current_config) {
          case CONFIG_IDLE_TYPE: {
            switch(input) {
              case IDLE_TYPE_OFF:
                idle_type = IdleType::OFF;
                break;
              case IDLE_TYPE_STATIC:
                idle_type = IdleType::STATIC;
                break;
              case IDLE_TYPE_SLOW:
                idle_type = IdleType::SLOW;
                break;
              case IDLE_TYPE_FAST:
                idle_type = IdleType::FAST;
                break;
            }

            reset_inputs();
            break;
          }
          case CONFIG_GROUND_EFFECTS: {
            switch(input) {
              case GROUND_EFFECTS_OFF:
                ground_effects = GroundEffects::OFF;
                break;
              case GROUND_EFFECTS_MATCH_IDLE:
                ground_effects = GroundEffects::MATCH_IDLE;
                break;
              case GROUND_EFFECTS_CLOCK:
                ground_effects = GroundEffects::CLOCK;
                break;
              case GROUND_EFFECTS_PULSE:
                ground_effects = GroundEffects::PULSE;
                break;
            }

            reset_inputs();
            break;
          }
        }

        break;
      }
      default:
        // We shouldn't get here once all the commands are coded, but if we
        // do, just reset.
        reset_inputs();
    }
  }
}

/** Resets the serial communication state machine. */
void reset_inputs() {
  current_command = ' ';
  current_config = ' ';
}

// The time at which the last idle cycle began.  Used to track when we need to
// start another color fade.
unsigned long last_idle_cycle_began = 0;
// How many cycles we've gone.  This is modulo'd to get the light order when we
// aren't actively fading colors.
int cycle_count = 0;

void do_idle_animation() {
  unsigned long now_millis = millis();

  bool advance_cycle = do_cabin_lights(now_millis, idle_type, current_idle);
  do_ground_effects(now_millis, ground_effects, idle_type, current_idle);

  // Apply whatever just happened.
  strip.show();

  // Finally, if we've completed the fade, reset the clock.
  if(advance_cycle) {
    last_idle_cycle_began = now_millis;
    cycle_count++;
  }
}

bool do_cabin_lights(unsigned long now_millis, IdleType idle_type, Shift shift) {
  if(shift == Shift::INVALID) {
    // If we don't have shift data yet, ignore it.  This will keep it in rainbow
    // mode until the first update hits, which will be a pretty good indicator
    // that data hasn't arrived.
    return false;
  }

  if(idle_type == IdleType::OFF) {
    // Idle's off, so turn off all the lights and ignore the rest of the
    // function.
    strip.fill(COLOR_OFF, 0, CABIN_LIGHT_COUNT);
    return false;
  }

  int shift_colors[IDLE_COLORS_ARR_LEN];
  get_shift_colors(shift, shift_colors, IDLE_COLORS_ARR_LEN);

  if(idle_type == IdleType::STATIC) {
    // Idle's static, so just fill it with the necessary colors.
    for(int i = 0; i < CABIN_LIGHT_COUNT; i++) {
      strip.setPixelColor(i, shift_colors[i % IDLE_COLORS_ARR_LEN]);
    }
    return false;
  }

  if(idle_type == IdleType::FAST || idle_type == IdleType::SLOW) {
    return do_blended_lights(0, CABIN_LIGHT_COUNT - 1, now_millis, shift_colors, 4);
  }

  // We shouldn't get here, but if we bottom out of the enum, return false.
  return false;
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

bool do_blended_lights(int start, int end, unsigned long now_millis, const int *colors, int color_size) {
  unsigned long time_since_last_cycle = now_millis - last_idle_cycle_began;

  if(time_since_last_cycle < IDLE_CYCLE_TIME_MILLIS) {
    // We're in the static part of the cycle.
    for(int i = start; i <= end; i++) {
      strip.setPixelColor(i, colors[(i + cycle_count) % color_size]);
    }
    return false;
  } else {
    // We're somewhere in the cycle.  Let's figure out how much.
    int cycle_time = IDLE_ROTATE_SLOW_TIME_MILLIS;
    if(idle_type == IdleType::FAST) cycle_time = IDLE_ROTATE_FAST_TIME_MILLIS;

    // I hope these values are named clearly enough.
    unsigned long this_fade_ends = last_idle_cycle_began + IDLE_CYCLE_TIME_MILLIS + cycle_time;

    // Calculate the percent of time that's passed since this fade began and how
    // long it should last.  This WILL likely wind up being over 1.0 eventually;
    // this is okay, as that'll hit the clamp.
    float amount = (float)(cycle_time - (this_fade_ends - now_millis)) / (float)cycle_time;

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

    // Do we need to update the cycle count?  Let's find out!
    return amount >= 1.0;
  }
}
