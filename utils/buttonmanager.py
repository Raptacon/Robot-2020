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

    _entries_container = []
    entries = {}

    def __init__(self, controller):
        self.controller = controller

    def __enter__(self):
        return self._entries_container.append

    def __exit__(self, *err_args):
        self.entries.update({self.controller: self._entries_container})

    @staticmethod
    def _run(controller, button, condition, action):

        action_map = {
            ButtonEvent.kOnPress: controller.getRawButtonPressed(button),
            ButtonEvent.kOnRelease: controller.getRawButtonReleased(button),
            ButtonEvent.kWhilePressed: controller.getRawButton(button),
            ButtonEvent.kWhileReleased: not controller.getRawButton(button)
        }

        if action_map[condition]:
            action()

    @classmethod
    def update_buttons(cls):
        all_entries = cls.__dict__.get("entries")
        for controller, entries in all_entries.items():
            for entry in entries:
                button, condition, action = entry
                cls._run(controller, button, condition, action)


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
