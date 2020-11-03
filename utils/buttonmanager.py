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


# # TESTING =================================================

# # HACK emulate enum values in methods
# #      to take arguments.
# class AxisEvent:

#     @staticmethod
#     def kLessThan(value):
#         return value

#     @staticmethod
#     def kGreaterThan(value):
#         return value

#     @staticmethod
#     def kAtValue(value):
#         return value

# class Axis(XboxController.Axis):
#     """
#     Xbox controller axis.
#     """

# class InputManager(_InputManager):

#     def __init__(self, controller):
#         pass

#     def __register(self, input_type, condition, action):
#         pass

#     def __enter__(self):
#         return self.__register

#     def __exit__(self, *err_args):
#         pass

# class AxisManager(_InputManager):

#     def __init__(self, controller):
#         pass

#     def __register(self, axis, condition, action):
#         pass

#     def __enter__(self):
#         return self.__register

#     def __exit__(self, *err_args):
#         pass

# # TESTING =================================================
