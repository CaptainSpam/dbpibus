#!/usr/bin/env python3

import time
import os
import board
import digitalio
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

_BACK_PIN = board.D26
_MINUS_PIN = board.D6
_PLUS_PIN = board.D5
_SELECT_PIN = board.D16

@dataclass(frozen=True)
class ButtonData:
    """The state of the buttons at an instant in time.  Note that the buttons
    (and, for that matter, the menu system they control) are based heavily on
    four-button pinball table service panels common since the 90s or so."""

    # Back/Service Credit button (the leftmost button).  Service Credit,
    # obviously, isn't particularly useful in this case, but I want it there for
    # easter egg purposes.
    back: bool = False

    # Minus button (second from the left).
    minus: bool = False

    # Plus button (third from the left).
    plus: bool = False

    # Menu/Select button (the right most button).  Both enters the menus and
    # acts as a confirm or go-forward button.
    select: bool = False

class ButtonHandler:
    """Initializes the buttons and provides an interface for reading them.  At
    time of writing, it's not much, but keeping it in a class like this might
    make things like debouncing easier later, if need be."""
    _back_button = None
    _minus_button = None
    _plus_button = None
    _select_button = None

    def __init__(self):
        logger.info('Initializing ButtonHandler!')
        logger.debug(f'Pins: back={_BACK_PIN}; minus={_MINUS_PIN}; plus={_PLUS_PIN}; select={_SELECT_PIN}')

        # Buttons up!
        self._back_button = digitalio.DigitalInOut(_BACK_PIN)
        self._back_button.direction = digitalio.Direction.INPUT
        self._back_button.pull = digitalio.Pull.UP

        self._minus_button = digitalio.DigitalInOut(_MINUS_PIN)
        self._minus_button.direction = digitalio.Direction.INPUT
        self._minus_button.pull = digitalio.Pull.UP

        self._plus_button = digitalio.DigitalInOut(_PLUS_PIN)
        self._plus_button.direction = digitalio.Direction.INPUT
        self._plus_button.pull = digitalio.Pull.UP

        self._select_button = digitalio.DigitalInOut(_SELECT_PIN)
        self._select_button.direction = digitalio.Direction.INPUT
        self._select_button.pull = digitalio.Pull.UP

    def get_button_state(self):
        return ButtonData(back = not self._back_button.value,
                          minus = not self._minus_button.value,
                          plus = not self._plus_button.value,
                          select = not self._select_button.value)
