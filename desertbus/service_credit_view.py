#!/usr/bin/env python3

import logging
from desertbus.vst_data import VstData, needs_service_dot
from desertbus.simple_animation_view import SimpleAnimationView
from desertbus.button_handler import ButtonData
import adafruit_character_lcd.character_lcd as characterlcd

logger = logging.getLogger(__name__)

class ServiceCreditView(SimpleAnimationView):
    """An easter egg view for pressing the back button from NormalView.  It has
    to be a separate class from SimpleAnimationView due to needing to check for
    the service dot like NormalView does."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        super().__init__(lcd, [], "", 10)
        logger.info(f"Initializing ServiceCreditView!")
        self._anim_deque = None

    @property
    def name(self):
        return f'ServiceCreditView'

    def _generate_animation(self, data: VstData) -> list:
        free_play_text = f'FREE PLAY{'.' if needs_service_dot(data) else ''}'.center(16)
        press_start_text = 'PRESS START'.center(16)
        blank_text = '                '

        anim_sequence = []
        for i in range(8):
            anim_sequence.append((300, free_play_text, press_start_text))
            anim_sequence.append((200, free_play_text, blank_text))

        return anim_sequence

    def handle_buttons(self, data: any, buttons: ButtonData) -> bool:
        # Wait!  We handle a button here!  Specifically, we handle if the user
        # presses Service Credit again by resetting the animation.
        if not self._previous_buttons is None:
            if buttons.back and not self._previous_buttons.back:
                logger.info('Back was pressed, restarting Free Play animation...')
                self._anim_deque = self._prepare_animation(self._generate_animation(data))

        # Beyond this, just let SimpleAnimationView handle it, which it will
        # likely do by updating _previous_buttons and maybe clearing the
        # animation with the Menu/Select button.
        return super().handle_buttons(data, buttons)

    def next_frame(self, data: any) -> bool:
        if self._anim_deque is None:
            self._anim_deque = self._prepare_animation(self._generate_animation(data))

        return self._do_animation_frame(self._anim_deque)
