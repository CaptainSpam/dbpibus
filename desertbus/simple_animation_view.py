#!/usr/bin/env python3

from desertbus.base_view import BaseView
import logging
import time
from collections import deque
import adafruit_character_lcd.character_lcd as characterlcd
from desertbus.button_handler import ButtonData

logger = logging.getLogger(__name__)

class SimpleAnimationView(BaseView):
    """A view that does a simple animation, then exits.

    This depends heavily on the anim_sequence parameter.  That's a list of
    three-element tuples in the form (duration_millis, line1, line2), where
    duration_millis is the time (in millis) the frame should last, and line1 and
    line2 are the two lines to be displayed."""
    def __init__(self,
                 lcd: characterlcd.Character_LCD,
                 anim_sequence: list,
                 name: str="Unnamed Animation",
                 priority: int=10):
        super().__init__(lcd)
        logger.info(f"Initializing SimpleAnimationView ({name})!")
        self._name = name
        self._priority = priority
        self._anim_sequence = anim_sequence
        self._anim_deque = None
        self._previous_buttons = None

    @property
    def priority(self):
        return self._priority
    
    @property
    def name(self):
        return f'SimpleAnimationView ({self._name})'
    
    def _prepare_animation(self, anim_list: list, start_time_millis=None) -> deque:
        """Prepares a list of animation commands for execution.  This returns a
        deque copy of the list where the first value in the tuple is each
        real-world timestamp at which the animation should occur, assuming it
        starts immediately, and should be fed into _do_animation_frame() to
        execute the next frame as need be.  If you want to base it on some other
        time, set start_time_millis accordingly."""
        next_time_millis = start_time_millis
        if next_time_millis is None:
            next_time_millis = time.time() * 1000

        result = deque()

        for (time_millis, line1, line2) in anim_list:
            if line1 is None or line2 is None:
                raise ValueError("Animation lines can't be None!")
            result.append((next_time_millis, line1, line2))
            next_time_millis = next_time_millis + time_millis

        # The last frame will have the time, but Nones for lines, to indicate it
        # should wait for the last frame and then stop.
        result.append((next_time_millis, None, None))

        return result

    def _do_animation_frame(self, anim_deque: deque) -> bool:
        """Executes an animation frame.  Once a frame expires, it's removed from
        the deque.  Once the deque is empty (or rather, once it runs into an
        entry where the lines are Nones), this returns True.  Otherwise, this
        returns False.  So, if this is a pure animation view (which most uses of
        this will be), the result of _do_animation_frame() can generally be used
        as the return value of next_frame().

        Note that this DOES change anim_deque as it processes frames."""
        if len(anim_deque) == 0:
            # If the deque is empty already, we're likely bailing out of an in-
            # progress animation.
            logger.info('anim_deque is empty, bailing out of animation...')
            return True

        current_time_millis = time.time() * 1000

        # Step one, find the current frame.
        current_frame = anim_deque[0]
        while len(anim_deque) > 1 and anim_deque[1][0] < current_time_millis:
            # If the NEXT frame is due, remove the lead from the queue and try
            # again.
            current_frame = anim_deque.popleft()

        if len(anim_deque) == 0 or current_frame[1] is None or current_frame[2] is None:
            # If the deque is empty at this point or we've reached the None/None
            # sentinel value, we're done with the animation.
            return True

        # Display the frame!
        self._display_text(current_frame[1], current_frame[2])
        return False

    def handle_buttons(self, data: any, buttons: ButtonData) -> bool:
        if buttons.select and (self._previous_buttons is None or not self._previous_buttons.select):
            # If Menu/Select is pressed, bail out of the view right away.
            logger.info('Select was pressed, clearing anim_deque...')
            self._anim_deque.clear()

        # In any case, we just eat the button.
        self._previous_buttons = buttons
        return True

    def next_frame(self, data: any) -> bool:
        if self._anim_deque is None:
            self._anim_deque = self._prepare_animation(self._anim_sequence)

        return self._do_animation_frame(self._anim_deque)
