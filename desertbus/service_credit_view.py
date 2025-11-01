#!/usr/bin/env python3

import logging
from desertbus.vst_data import VstData
from desertbus.simple_animation_view import SimpleAnimationView
from desertbus.normal_view import _needs_service_dot
import adafruit_character_lcd.character_lcd as characterlcd

logger = logging.getLogger(__name__)

class ServiceCreditView(SimpleAnimationView):
    """An easter egg view for pressing the back button from NormalView.  It has
    to be a separate class from SimpleAnimationView due to needing to check for
    the service dot like NormalView does."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        super().__init__(lcd, [], "", 5)
        logger.info(f"Initializing ServiceCreditView!")
        self._anim_deque = None
    
    @property
    def name(self):
        return f'ServiceCreditView'
    
    def _generate_animation(self, data: VstData) -> list:
        free_play_text = f'FREE PLAY{'.' if _needs_service_dot(data) else ''}'.center(16)
        press_start_text = 'PRESS START'.center(16)
        blank_text = '                '

        anim_sequence = []
        for i in range(8):
            anim_sequence.append((300, free_play_text, press_start_text))
            anim_sequence.append((200, free_play_text, blank_text))

        return anim_sequence

    def next_frame(self, data: any) -> bool:
        if self._anim_deque is None:
            self._anim_deque = self._prepare_animation(self._generate_animation(data))

        return self._do_animation_frame(self._anim_deque)
