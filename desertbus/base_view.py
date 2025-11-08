#!/usr/bin/env python3

from abc import ABC, abstractmethod
import time
import adafruit_character_lcd.character_lcd as characterlcd
from desertbus.button_handler import ButtonData

class BaseView(ABC):
    """The basic abstract view from which other views derive."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        self._advance_frame_time()
        self._lcd = lcd
        self._previous_buttons = None

    @property
    @abstractmethod
    def priority(self):
        """The view's priority.  Lower numbers mean higher priority."""
        pass

    @property
    def name(self):
        """The name of the view, suitable for the logger."""
        return self.__class__.__name__

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

    def handle_buttons(self, data: any, buttons: ButtonData) -> any:
        """Handles button input.  This returns a new view if the main loop needs
        to add it to the queue, or None if nothing needs to be done."""
        self._previous_buttons = buttons
        return None

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
