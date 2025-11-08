#!/usr/bin/env python3

import logging
import time
from enum import Enum, auto
from abc import ABC, abstractmethod
from desertbus.vst_data import VstData
from desertbus.base_view import BaseView
from desertbus.button_handler import ButtonData
from desertbus.simple_animation_view import SimpleAnimationView
from desertbus.shift_data import Shift, make_view_for_shift
from desertbus.event_data import Event, make_view_for_event
import adafruit_character_lcd.character_lcd as characterlcd
from desertbus.config import load_config, get_setting, set_setting, ConfigKey, ShiftAnim, LcdColor, EventAnim

logger = logging.getLogger(__name__)

_SAVE_DISPLAY_MILLIS = 1000

class _ReturnType(Enum):
    """The various things that can be returned from a button interaction."""
    # The view should stay at this menu item.
    STAY_HERE = auto()
    # The view should push a menu item to the stack; the second return value
    # will be the menu item to push.
    PUSH_MENU = auto()
    # This menu item is done, so the view should pop it from the stack and
    # continue with the previous menu item, or exit if the stack is now empty.
    POP_STACK = auto()
    # This menu item is requesting the main loop display another view; the
    # second return value will be the new view to push.
    GO_TO_VIEW = auto()

class _NodeType(Enum):
    """The types of nodes, used when constructing new ones during navigation."""
    # A ContainerNode, used for making the node structure.
    CONTAINER = auto()
    # A SettingNode, which sets settings.
    SETTING = auto()
    # A TestNode, which has a list of tests which can be triggered to show new
    # views (almost certainly SimpleAnimationViews).
    TESTS = auto()

class _TestView(Enum):
    """The types of views that can be tested."""
    # Dawn Guard transition.
    SHIFT_DAWN_ANIM = auto()
    # Alpha Flight transition.
    SHIFT_ALPHA_ANIM = auto()
    # Night Watch transition.
    SHIFT_NIGHT_ANIM = auto()
    # Zeta Shift transition.
    SHIFT_ZETA_ANIM = auto()
    # Omega Shift transition.
    SHIFT_OMEGA_ANIM = auto()
    # Point Get event animation.
    EVENT_POINT_ANIM = auto()
    # Crash event animation.
    EVENT_CRASH_ANIM = auto()
    # Bug Splat event animation.
    EVENT_SPLAT_ANIM = auto()
    # Bus Stop event animation.
    EVENT_STOP_ANIM = auto()

class _MenuNode(ABC):
    """Some manner of menu node.  This is the good stuff.  Or, rather, the base
    of the good stuff."""
    def __init__(self, title: str):
        self._title = title

    @property
    def title(self) -> str:
        """This node's title.  Will be displayed when selecting child nodes."""
        return self._title

    @abstractmethod
    def handle_buttons(self, buttons: ButtonData) -> (_ReturnType, any):
        """Does whatever needs doing with the given buttons.  Returns some enum
        for whatever behavior needs to happen, plus bonus data if need be."""
        pass

    @abstractmethod
    def get_current_display(self) -> (str, str):
        """Gets the text to be displayed, as two separate lines."""
        pass

class _ContainerNode(_MenuNode):
    """A container node contains other nodes.  It's used to navigate the menu
    structure to something like a SettingNode."""
    def __init__(self, title: str, children: list):
        super().__init__(title)
        self._children = children
        self._current_index = 0

    def handle_buttons(self, buttons: ButtonData) -> (_ReturnType, any):
        if buttons.back:
            return (_ReturnType.POP_STACK, None)
        if buttons.select:
            new_node = _inflate_node(self._children[self._current_index])
            if not new_node is None:
                return (_ReturnType.PUSH_MENU, new_node)
        if buttons.minus:
            self._current_index -= 1

            if self._current_index < 0:
                self._current_index = len(self._children) - 1
        if buttons.plus:
            self._current_index += 1

            if self._current_index >= len(self._children):
                self._current_index = 0

        return (_ReturnType.STAY_HERE, None)

    def get_current_display(self) -> (str, str):
        # Top line is this node's title, bottom line is the current selection.
        return (self.title.ljust(16), self._children[self._current_index]['title'].rjust(16))

class _SettingNode(_MenuNode):
    """A node that represents a config setting."""
    def __init__(self, title: str, key: ConfigKey, options: list):
        super().__init__(title)
        self._key = key
        self._options = options
        self._current_index = 0
        self._save_time_millis = 0

        # Start on whatever the current selection is.
        initial_setting = get_setting(key)
        for option in options:
             if option['value'] == initial_setting:
                 break
             self._current_index += 1

        # If we don't find it, just start at zero.
        if self._current_index >= len(self._options):
            self._current_index = 0

    def _is_displaying_saved(self) -> bool:
        # If the current time is less than the time the user pressed save (plus
        # the timeout), then we're displaying saved.
        return time.time() * 1000 < (self._save_time_millis + _SAVE_DISPLAY_MILLIS)

    def handle_buttons(self, buttons: ButtonData) -> (_ReturnType, any):
        # Ignore any buttons if we're currently displaying the Saved! text.
        if self._is_displaying_saved():
            return (_ReturnType.STAY_HERE, None)

        if buttons.back:
            return (_ReturnType.POP_STACK, None)
        if buttons.select:
            # Aha!  The user wants THIS!
            logger.debug(f'Setting {self._key} to {self._options[self._current_index]['value']}...')
            set_setting(self._key, self._options[self._current_index]['value'])
            # Remember when the user saved.  We'll display "Saved!" for a bit.
            self._save_time_millis = time.time() * 1000
            return (_ReturnType.STAY_HERE, None)
        if buttons.minus:
            self._current_index -= 1

            if self._current_index < 0:
                self._current_index = len(self._options) - 1
        if buttons.plus:
            self._current_index += 1

            if self._current_index >= len(self._options):
                self._current_index = 0

        return (_ReturnType.STAY_HERE, None)

    def get_current_display(self) -> (str, str):
        # TODO: Maybe blink the selection?
        if self._is_displaying_saved():
            return (self.title.ljust(16), "     Saved!     ")

        return (self.title.ljust(16), self._options[self._current_index]['title'].rjust(16))

class _TestNode(_MenuNode):
    """A node that shows a list of tests to be executed when selected."""
    def __init__(self, title: str, tests: list):
        super().__init__(title)
        self._tests = tests
        self._current_index = 0

    def handle_buttons(self, buttons: ButtonData) -> (_ReturnType, any):
        if buttons.back:
            return (_ReturnType.POP_STACK, None)
        if buttons.select:
            # A test!
            logger.debug(f'Starting test animation {self._tests[self._current_index]['title']}...')
            return (_ReturnType.GO_TO_VIEW, self._tests[self._current_index]['type'])
        if buttons.minus:
            self._current_index -= 1

            if self._current_index < 0:
                self._current_index = len(self._tests) - 1
        if buttons.plus:
            self._current_index += 1

            if self._current_index >= len(self._tests):
                self._current_index = 0

        return (_ReturnType.STAY_HERE, None)

    def get_current_display(self) -> (str, str):
        # All we need is the title and test name.  A test will, by definition,
        # replace the display, and when it's done, we'll just be back at the
        # menu anyway.
        return (self.title.ljust(16), self._tests[self._current_index]['title'].rjust(16))

class _TopLevel(_MenuNode):
    """The top of the menu.  It just displays the program name, the version, and
    a message to press MENU to continue."""
    def handle_buttons(self, buttons: ButtonData) -> _ReturnType:
        if buttons.select:
            return (_ReturnType.PUSH_MENU, _inflate_node(_NODE_STRUCTURE))
        if buttons.back:
            return (_ReturnType.POP_STACK, None)
        return (_ReturnType.STAY_HERE, None)

    def get_current_display(self) -> (str, str):
        return (" dbpibus v0.7.0 ","   Press Menu   ")

def _inflate_node(node: dict) -> _MenuNode:
    """Inflates a node from a dict structure."""
    match node["type"]:
        case _NodeType.CONTAINER:
            return _ContainerNode(
                title = node["title"],
                children = node["children"]
            )
        case _NodeType.SETTING:
            return _SettingNode(
                title = node["title"],
                key = node["key"],
                options = node["options"]
            )
        case _NodeType.TESTS:
            return _TestNode(
                title = node["title"],
                tests = node["tests"]
            )
        case _:
            logger.error(f'{node["type"]} is not a valid node type!')
            return None

_NODE_STRUCTURE = {
    "type": _NodeType.CONTAINER,
    "title": "Main Menu",
    "children": [
        {
            "type": _NodeType.CONTAINER,
            "title": "Adjustments",
            "children": [
                {
                    "type": _NodeType.SETTING,
                    "title": "Show Shift Anims",
                    "key": ConfigKey.SHOW_SHIFT_ANIM,
                    "options": [
                        { "title": "Always", "value": ShiftAnim.ALWAYS },
                        { "title": "Only in-season", "value": ShiftAnim.ONLY_IN_SEASON },
                        { "title": "Never", "value": ShiftAnim.NEVER },
                    ]
                },
                {
                    "type": _NodeType.SETTING,
                    "title": "Show Event Anims",
                    "key": ConfigKey.SHOW_EVENT_ANIM,
                    "options": [
                        { "title": "Always", "value": EventAnim.ALWAYS },
                        { "title": "Never", "value": EventAnim.NEVER },
                    ]
                },
                {
                    "type": _NodeType.SETTING,
                    "title": "LCD Color",
                    "key": ConfigKey.LCD_COLOR,
                    "options": [
                        { "title": "Current Shift", "value": LcdColor.CURRENT_SHIFT },
                        { "title": "Dawn Guard", "value": LcdColor.DAWN_GUARD },
                        { "title": "Alpha Flight", "value": LcdColor.ALPHA_FLIGHT },
                        { "title": "Night Watch", "value": LcdColor.NIGHT_WATCH },
                        { "title": "Zeta Shift", "value": LcdColor.ZETA_SHIFT },
                        { "title": "Omega Shift", "value": LcdColor.OMEGA_SHIFT },
                    ]
                }
            ]
        },
        {
            "type": _NodeType.CONTAINER,
            "title": "Tests",
            "children": [
                {
                    "type": _NodeType.TESTS,
                    "title": "Shift Anims",
                    "tests": [
                        {
                            "title": "Dawn Guard",
                            "type": _TestView.SHIFT_DAWN_ANIM,
                        },
                        {
                            "title": "Alpha Flight",
                            "type": _TestView.SHIFT_ALPHA_ANIM,
                        },
                        {
                            "title": "Night Watch",
                            "type": _TestView.SHIFT_NIGHT_ANIM,
                        },
                        {
                            "title": "Zeta Shift",
                            "type": _TestView.SHIFT_ZETA_ANIM,
                        },
                        {
                            "title": "Omega Shift",
                            "type": _TestView.SHIFT_OMEGA_ANIM,
                        },
                    ]
                },
                {
                    "type": _NodeType.TESTS,
                    "title": "Event Anims",
                    "tests": [
                        {
                            "title": "Point Get",
                            "type": _TestView.EVENT_POINT_ANIM,
                        },
                        {
                            "title": "Crash",
                            "type": _TestView.EVENT_CRASH_ANIM,
                        },
                        {
                            "title": "Bug Splat",
                            "type": _TestView.EVENT_SPLAT_ANIM,
                        },
                        {
                            "title": "Bus Stop",
                            "type": _TestView.EVENT_STOP_ANIM,
                        },
                    ]
                },
            ]
        }
    ]
}

class ServiceMenuView(BaseView):
    """The entire service menu, as a view."""
    def __init__(self, lcd: characterlcd.Character_LCD):
        super().__init__(lcd)
        logger.info(f"Initializing ServiceMenuView!")
        self._menu_stack = [_TopLevel("Top Level")]

    @property
    def priority(self) -> int:
        # The menu should override everything, EXCEPT if it's testing animation
        # views.  Zero should do the trick for now.
        return 0

    def _get_test_view(self, test_view: _TestView) -> SimpleAnimationView:
        """Gets a view for a test."""
        match test_view:
            case _TestView.SHIFT_DAWN_ANIM:
                return make_view_for_shift(self._lcd, Shift.DAWN_GUARD, -1)
            case _TestView.SHIFT_ALPHA_ANIM:
                return make_view_for_shift(self._lcd, Shift.ALPHA_FLIGHT, -1)
            case _TestView.SHIFT_NIGHT_ANIM:
                return make_view_for_shift(self._lcd, Shift.NIGHT_WATCH, -1)
            case _TestView.SHIFT_ZETA_ANIM:
                return make_view_for_shift(self._lcd, Shift.ZETA_SHIFT, -1)
            case _TestView.SHIFT_OMEGA_ANIM:
                return make_view_for_shift(self._lcd, Shift.OMEGA_SHIFT, -1)
            case _TestView.EVENT_POINT_ANIM:
                return make_view_for_event(self._lcd, Event.POINT, -1)
            case _TestView.EVENT_SPLAT_ANIM:
                return make_view_for_event(self._lcd, Event.SPLAT, -1)
            case _TestView.EVENT_STOP_ANIM:
                return make_view_for_event(self._lcd, Event.STOP, -1)
            case _TestView.EVENT_CRASH_ANIM:
                return make_view_for_event(self._lcd, Event.CRASH, -1)

    def handle_buttons(self, data: any, buttons: ButtonData) -> any:
        if len(self._menu_stack) == 0:
            # Whoops.  The menu stack's empty.  Just forget it; next_frame will
            # close us out.
            return True

        # If the last-known buttons are None, take whatever's pressed as the
        # first and ignore further processing.  That oughta stop us from
        # skipping right past _TopLevel at the start.
        if not self._previous_buttons is None and not self._previous_buttons == buttons:
            (rtype, extra) = self._menu_stack[-1].handle_buttons(buttons)

            match rtype:
                case _ReturnType.POP_STACK:
                    logger.debug(f'Popping {self._menu_stack[-1]} from the stack...')
                    self._menu_stack.pop()

                    # If the only thing left in the stack is TopLevel, remove it
                    # too.
                    if len(self._menu_stack) == 1:
                        self._menu_stack.pop()
                case _ReturnType.PUSH_MENU:
                    logger.debug(f'Pushing {extra} onto the stack...')
                    self._menu_stack.append(extra)
                case _ReturnType.GO_TO_VIEW:
                    logger.debug(f'Telling the main loop to show {extra}...')
                    # We have to update _previous_buttons here, as we're
                    # returning here, too.
                    self._previous_buttons = buttons
                    return self._get_test_view(extra)

        # After processing, remember the last-known buttons.
        self._previous_buttons = buttons
        return True

    def next_frame(self, data: any) -> bool:
        if len(self._menu_stack) == 0:
            logger.debug('Stack is empty, exiting menu...')
            return True

        (line1, line2) = self._menu_stack[-1].get_current_display()
        self._display_text(line1, line2)

        return False
