#include <Adafruit_NeoPixel.h>
#include "colors.h"
#include "serial_constants.h"
#include "enum_constants.h"

const int NEOPIXEL_PIN = 16;
const int NEOPIXEL_STRAND_LENGTH = 20;
Adafruit_NeoPixel strip(NEOPIXEL_STRAND_LENGTH, NEOPIXEL_PIN);

int current_idle = SHIFT_INVALID;

void setup() {
  // Fire up some serial!
  Serial.begin(9600);

  // NeoPixels start up now, too!  By which I mean they don't start up, they
  // turn off if they were on.
  strip.begin();
  strip.show();
  strip.setBrightness(50);
}

void loop() {
  // TODO: Everything, really.
}

void read_serial() {
  if(Serial.available()) {
    // We got something!  It'll be a single character command.  Further data
    // will be dependent on the command.
    char command = (char)Serial.read();

    // TODO: Do something with it!  We'll be updating globals with the result of
    // whatever we got.  Remember, in each case we're expecting the next byte to
    // be available right away.
    switch(command) {
      case COMMAND_EVENT_ANIMATION:
        break;
      case COMMAND_STOP_EVENT:
        break;
      case COMMAND_SET_IDLE_ANIMATION:
        // Next character is what shift we're becoming.  Turn it into an int.
        char shift = (char)Serial.read();

        switch(shift) {
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
          default:
            // This wasn't a valid animation.  Hold steady.
            return;
        }

        break;
      case COMMAND_UPDATE_CONFIG:
        break;
      default:
        // We got an invalid command, so ignore it and bail out.
        return;
    }
  }
}
