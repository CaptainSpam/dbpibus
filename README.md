# dbpibus

A Desert Bus for Hope Raspberry Pi project.

This repository keeps track of the progress of this weird idea I had to make a craftalong project for Desert Bus for Hope.  It'll involve a Raspberry Pi, an LED character display, a few RGB LEDs, a bus-shaped shell around it, and it'll look neat.

Ultimately, this won't be very useful to anyone else unless they have a list of parts I intend to use, which I'm still hashing out.  At the very least, the current plan involves:

- A Raspberry Pi Zero 2 W
- Adafruit's RGB backlight negative LCD 16x2 + extras - RGB on black (https://adafru.it/399)
- A Raspberry Pi Pico 2
- Some amount of Adafruit Neopixels

There are also buttons, an IC, and a couple odd electrical components, too, but the specifics are still up for debate.  I'll inventory what I'm using eventually.

The current structure of the repo:

- `dbpibus.py` is what you launch on the Zero.  That starts up the LCD and data fetching.
- `dbpibus.service` is a systemd service to launch `dbpibus.py` at boot time.
- `desertbus/` contains the rest of the Python bits referenced from `dbpibus.py`.
- `dbpibus_leds/` contains the Arduino C++ code for the Pico.

There's obviously some Python modules and such needed, which I will document later, once I've got time.
