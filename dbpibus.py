#!/usr/bin/env python3

# Desert Bus for Hope Home Verisimilator Project
# (aka dbpibus)
# (c)2025 Nicholas Killewald
# Distributed under the terms of the MIT License.
# A "LICENSE" file is included in the top level of the source distribution.

from datetime import datetime
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import pwmio
import time
from time import sleep
import os
import heapq
import logging
from logging.handlers import RotatingFileHandler
from desertbus.normal_view import NormalView
from desertbus.service_credit_view import ServiceCreditView
from desertbus.fetcher_thread import FetcherThread
from desertbus.shift_data import get_current_shift, SCREEN_COLORS, Shift, make_view_for_shift
from desertbus.button_handler import ButtonHandler
from desertbus.event_data import make_views_for_events

# Get a logger going.
log_file = f"{os.path.expanduser('~')}/dbpibus.log"
log_format = logging.Formatter('%(asctime)s %(levelname)s [%(threadName)s] [%(module)s] %(funcName)s(%(lineno)d): %(message)s')

handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=10, encoding=None, delay=0)
handler.setFormatter(log_format)
handler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Say hello to the nice people, dbpibus.
logger.info("Welcome to CaptainSpam's Desert Bus for Hope Home Verisimulator Project.")

# Set up the LCD.
logger.info("Initializing everything for a 2x16 LCD...")
lcd_columns = 16
lcd_rows = 2

lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D27)

# RGB pins!
red = pwmio.PWMOut(board.D21)
green = pwmio.PWMOut(board.D12)
blue = pwmio.PWMOut(board.D18)

# Our precious LCD object.  Take good care of it.
lcd = characterlcd.Character_LCD_RGB(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows, red, green, blue)

# Clear the LCD and start it off with the current shift color, solely by the
# clock.  If we need Omega, we'll get that on the first data fetch.
lcd.clear()
current_shift = get_current_shift()
logger.info(f'Starting off with {current_shift}...')
lcd.color = SCREEN_COLORS[current_shift]

# And a starter message until the data comes in.
lcd.message = "Your driver is:".center(16) + "\n" + "JOCKO".center(16)

# Ready the buttons!
button_handler = ButtonHandler()
previous_buttons = None

# Our view queue.  Or, well, heap.  I know it looks like a list now, but trust
# me, it'll be a queue.  Heap.  Heapy queue.
views = []

# Kick the thread into action.
t = FetcherThread('FetcherThread')
t.start()

logger.info('Ready.  Your driver is: JOCKO')
# At least say something on the console so we know we're live.
print('Your driver is: JOCKO')

is_aware_of_dead_fetcher_thread = False
previous_stats = None

while True:
    latest_stats = t.latest_stats
    # Check if we're in Omega yet.  Y'know, if there's stats at all.  Note that
    # if the Omega flag is None, *don't change out of Omega*.  None means there
    # was some problem fetching the Omega state, not that Omega is over (likely
    # meaning we're in the offseason).  The ONLY way we leave Omega is if the
    # flag is EXPLICITLY False.  If we were in Omega and got a None, stay in
    # Omega.
    now_shift = None
    if (latest_stats is not None
        and (latest_stats.is_omega_shift is True
            or (latest_stats.is_omega_shift is None and now_shift == Shift.OMEGA_SHIFT))):
        now_shift = Shift.OMEGA_SHIFT
    else:
        now_shift = get_current_shift()
    if not now_shift == current_shift:
        logger.info(f'Shift change!  Changing from {current_shift} to {now_shift}...')

        # Set the screen color first.
        lcd.color = SCREEN_COLORS[now_shift]

        # Then, ONLY if we're not switching OFF of Omega, do the animation.  It
        # just wouldn't be right to do a transition coming off of the end of the
        # run.
        if not current_shift == Shift.OMEGA_SHIFT:
            heapq.heappush(views, make_view_for_shift(lcd, now_shift))

        current_shift = now_shift
    if latest_stats is not None:
        if len(views) == 0:
            # If this is the first pass or if NormalView somehow got removed
            # from the queue, put a new NormalView in.
            heapq.heappush(views, NormalView(lcd))

        # Handle any buttons first.
        buttons = button_handler.get_button_state()
        if not views[0].handle_buttons(latest_stats, buttons):
            # The view didn't handle it (which is the most common case).  It's
            # up to us!

            # First, check for the easter egg.  Only do this if the back button
            # wasn't already pressed in the previous frame (so holding back
            # won't just keep triggering ServiceCreditView).
            if buttons.back and (previous_buttons is None or not previous_buttons.back):
                logger.info('Back was pressed outside of the menus, adding ServiceCreditView to the queue...')
                heapq.heappush(views, ServiceCreditView(lcd))
            elif buttons.select and (previous_buttons is None or not previous_buttons.select):
                # TODO: Handle the menu.
                pass

        # Check for events (if the run is live); add those in if need be.
        if latest_stats.is_live:
            event_views = make_views_for_events(lcd, previous_stats, latest_stats)
            if len(event_views) > 0:
                for event_view in event_views:
                    logger.info(f'Event occurred!  Adding {event_view} to the queue...')
                    heapq.push(views, event_view)

        # Then, handle the next frame.
        if views[0].next_frame(latest_stats):
            # This view just finished up, so pop it away.
            logger.info(f'View {views[0].name} complete, removing from queue...')
            heapq.heappop(views)

        # Stash away the previous stats for the next event check.
        previous_stats = latest_stats

    if not t.is_alive() and not is_aware_of_dead_fetcher_thread:
        logger.critical("THE FETCHER THREAD ISN'T RUNNING!  THIS IS REALLY BAD!")
        # TODO: Maybe restart the thread?  This really, REALLY shouldn't happen,
        # so there's a chance we're in a super bad state somehow.
        is_aware_of_dead_fetcher_thread = True

    sleep(0.035)
