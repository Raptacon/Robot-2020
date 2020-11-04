from enum import Enum, auto
from wpilib import XboxController


class Button(XboxController.Button):
    """
    Xbox controller buttons.
    """


class ButtonEvent(Enum):
    """
    Supported button events.
    """

    kOnPress = auto()
    kOnRelease = auto()
    kWhilePressed = auto()
    kWhileReleased = auto()

class ButtonManager:

    _tmp_container = []
    controllers = []
    entries = {}

    # _entries_container = []
    # entries = {}
 
    def __init__(self):
        pass

    def __enter__(self):
        return self._tmp_container.append

    def _create_final(self, controller, button, condition, action):
        if controller not in self.entries:
            self.entries[controller] = {}
        if button not in self.entries[controller]:
            self.entries[controller][button] = []

        self.entries[controller][button].append([condition, action])

    def __exit__(self, *err_args):
        for entry in self._tmp_container:
            controller, button, condition, action = entry
            self._create_final(controller, button, condition, action)

    @staticmethod
    def _run(controller, button, actions):

        action_map = {
            ButtonEvent.kOnPress: controller.getRawButtonPressed(button),
            ButtonEvent.kOnRelease: controller.getRawButtonReleased(button),
            ButtonEvent.kWhilePressed: controller.getRawButton(button),
            ButtonEvent.kWhileReleased: not controller.getRawButton(button)
        }

        for action in actions:
            condition, callable_ = action
            if action_map[condition]:
                callable_()
                print(f"executing button: {controller} {button} {condition} {callable_}")

    @classmethod
    def update_buttons(cls):

        for controller, events in cls.__dict__.get("entries").items():
            for button, actions in events.items():
                cls._run(controller, button, actions)

# NOTE this would be in robot.py
# from typing import List, Tuple
# def _register_buttons(self, events: List[Tuple[wpilib.XboxController, Button, ButtonEvent, callable]]=None):

#     with ButtonManager() as register:
#         for event in events:
#             register(event)


##### NOTES #####

#
# TODO: figure out how to support button events for other robots.
#       Right now this is exclusive to doof.
#
#       NOTE: This will likely need to be "brute-forced"
#             (chain of if-elif statements) because buttons
#             can't live in a config file and they have
#             to be explicitly listed here.
#
#             If we decide NOT to use multiple robots,
#             this won't be necessary.
#
# XXX: Should we handle buttons within individual components?
#      We could register buttons in the `on_enable` portion of
#      the components. This would allow buttons to be used on
#      different robots because when the components are disabled,
#      the button events won't be registered.
#
#      Or, we could have a buttons component that handles
#      button registration in the `on_enable` portion and
#      updates the axis in the `execute` portion. This
#      would eliminate the need to use threads to update
#      controllers.
#
# XXX: Injectables shouldn't be used in MyRobot. They are
#      designed for components.
#

#
# BIG NOTE: We shouldn't use a button manager. It's a really good idea for one robot,
#           but we don't know if we'll have more than one. Also, handling buttons in
#           the components (specifically the `execute` portion) is more explicit and
#           localized.
#
