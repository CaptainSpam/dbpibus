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

    def handle_buttons(self, data: any, buttons: ButtonData) -> bool:
        """Handles button input.  In general, most views will ignore this.  But,
        the operator menus will need this to deal with navigating the menu.
        This is called before next_frame().

        This should return False (the default) if this view didn't handle the
        buttons (and thus the main thread should do something with the input),
        True if it did (and thus the main thread should ignore the inputs)."""
        return False

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
