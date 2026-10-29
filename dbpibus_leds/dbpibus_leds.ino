#include "globals.h"
#include "serial_constants.h"
#include "enum_constants.h"
#include "idle.h"
#include "events.h"

int last_light = -1;
bool showing_lights = true;

Shift current_idle = Shift::INVALID;
IdleType idle_type = IdleType::SLOW;
GroundEffects ground_effects = GroundEffects::MATCH_IDLE;

char current_command = ' ';
char current_config = ' ';

unsigned long last_animation_began_millis = 0;
EventAnimation current_animation = EventAnimation::INVALID;

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
  // Zero otherwise absolutely won't finish booting before the Pico starts
  // running.
  request_config();
}

void loop() {
  unsigned long now_millis = millis();

  // Update all serial data as need be.
  read_serial();

  // Do any event animation, if one is available.  Otherwise, go with idle.
  if(!do_event_animation(current_animation, now_millis, last_animation_began_millis))
    do_idle_animation(now_millis);
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
