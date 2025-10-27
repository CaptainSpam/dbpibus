#!/usr/bin/env python3

from abc import ABC, abstractmethod
import time
from collections import deque
import adafruit_character_lcd.character_lcd as characterlcd

class BaseView(ABC):
    """The basic abstract view from which other views derive."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        self._advance_frame_time()
        self._lcd = lcd

    def _prepare_animation(self, anim_list: list, start_time_millis=None) -> deque:
        """Prepares a list of animation commands for execution.  Such a list
        should be a series of tuples in the form of (time_millis, line1, line2),
        where time_millis is the time (in millis) the frame should last, and
        line1 and line2 are the two strings to be displayed.  This returns a
        deque copy of that list where the first value in the tuple is each
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

    @property
    @abstractmethod
    def priority(self):
        """The view's priority.  Lower numbers mean higher priority."""
        pass

    def _advance_frame_time(self):
        """Advances the frame.  Which just means update the most recent frame
        timestamp."""
        self._last_frame_millis = round(time.time() * 1000)

    def _display_text(self, line1, line2):
        """Convenience method for displaying text to the screen."""
        self._lcd.message = line1 + "\n" + line2

    def __lt__(self, other):
        if not isinstance(other, BaseView):
            return NotImplemented
        return self.priority < other.priority

    @abstractmethod
    def next_frame(self, data: any) -> bool:
        """Process the next frame.  Exactly what this means is up to the
        implementation; it might just be repeating the same strings currently
        on-screen.

        There is no guarantee that a given view will handle the next frame that
        needs processing, even if the view isn't finished yet.  Any view can be
        interrupted by something of a higher (lower-numbered) priority, in which
        case the lower-priority view just won't get any next_frame calls until
        the higher-priority view finishes and yields control.  In fact, that's
        the entire way NormalView is intended to work.

        Returns True if this view is complete and should be disposed
        afterward (i.e. a transition animation is complete), False if there's
        still more to go (i.e. the animation isn't complete, or this is
        NormalView and shouldn't ever go away)."""
        pass
