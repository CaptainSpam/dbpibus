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

int last_light = -1;
bool showing_lights = true;

int current_idle = SHIFT_INVALID;
int idle_type = IDLE_STATIC;

char current_command = ' ';

void setup() {
  // TODO: Remove the serial monitor?
  Serial.begin(9600);
  Serial.println("SETUP COMPLETE");

  // Fire up some serial!
  Serial1.begin(9600);

  // NeoPixels start up now, too!  By which I mean they don't start up, they
  // turn off if they were on.
  strip.begin();
  strip.rainbow(0, 3);
  strip.show();
  strip.setBrightness(50);
}

void loop() {
  // Update all serial data as need be.
  read_serial();

  // Update the lights for the idle version.
  // TODO: Events take priority, so if there's one waiting, this should wait its
  // turn.
  do_idle_animation();
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
            current_idle = SHIFT_DAWNGUARD;
            break;
          case IDLE_ANIMATION_ALPHAFLIGHT:
            current_idle = SHIFT_ALPHAFLIGHT;
            break;
          case IDLE_ANIMATION_NIGHTWATCH:
            current_idle = SHIFT_NIGHTWATCH;
            break;
          case IDLE_ANIMATION_ZETASHIFT:
            current_idle = SHIFT_ZETASHIFT;
            break;
          case IDLE_ANIMATION_OMEGASHIFT:
            current_idle = SHIFT_OMEGASHIFT;
            break;
        }

        // Valid or not, reset the command back to a space.
        current_command = ' ';
      }
      default:
        // We shouldn't get here once all the commands are coded, but if we
        // do, just reset the command.
        current_command = ' ';
    }
  }
}



// The time at which the last idle cycle began.  Used to track when we need to
// start another color fade.
int last_idle_cycle_began = 0;
// How many cycles we've gone.  This is modulo'd to get the light order when we
// aren't actively fading colors.
int cycle_count = 0;

void do_idle_animation() {
  int now_millis = millis();

  if(idle_type == IDLE_OFF) {
    // Idle's off (or we don't have shift data yet), so turn off all the lights
    // and ignore the rest of the function.
    strip.fill();
    strip.show();
    last_idle_cycle_began = now_millis;
    return;
  }

  int shift_colors[4];
  get_shift_colors(current_idle, shift_colors, 4);

  if(idle_type == IDLE_STATIC) {
    // Idle's static, so just fill it with the necessary colors.
    for(int i = 0; i < CABIN_LIGHT_COUNT; i++) {
      strip.setPixelColor(i, shift_colors[i % IDLE_COLORS_ARR_LEN]);
    }
    strip.show();
    return;
  }

  int time_since_last_cycle = now_millis - last_idle_cycle_began;

  if(time_since_last_cycle < IDLE_CYCLE_TIME_MILLIS) {
    // We're in the static part of the cycle.
    for(int i = 0; i < CABIN_LIGHT_COUNT; i++) {
      strip.setPixelColor(i, shift_colors[(i + cycle_count) % IDLE_COLORS_ARR_LEN]);
    }
    strip.show();
  } else {
    // We're somewhere in the cycle.  Let's figure out how much.
    int cycle_time = IDLE_ROTATE_SLOW_TIME_MILLIS;
    if(idle_type == IDLE_FAST) cycle_time = IDLE_ROTATE_FAST_TIME_MILLIS;

    // I hope these values are named clearly enough.
    int this_fade_ends = last_idle_cycle_began + IDLE_CYCLE_TIME_MILLIS + cycle_time;

    // Calculate the percent of time that's passed since this fade began and how
    // long it should last.  This WILL likely wind up being over 1.0 eventually;
    // this is okay, as that'll hit the clamp.
    float amount = (float)(cycle_time - (this_fade_ends - now_millis)) / (float)cycle_time;

    // Then, build up a new array of blended colors.
    int faded_colors[4] = {
      blend_colors(shift_colors[0], shift_colors[1], amount),
      blend_colors(shift_colors[1], shift_colors[2], amount),
      blend_colors(shift_colors[2], shift_colors[3], amount),
      blend_colors(shift_colors[3], shift_colors[0], amount)
    };

    // NOW we can display them!
    for(int i = 0; i < CABIN_LIGHT_COUNT; i++) {
      strip.setPixelColor(i, faded_colors[(i + cycle_count) % IDLE_COLORS_ARR_LEN]);
    }
    strip.show();

    // Finally, if we've completed the fade, reset the clock.
    if(amount >= 1.0) {
      last_idle_cycle_began = now_millis;
      cycle_count++;
    }
  }
}
