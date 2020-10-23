from enum import Enum, auto
from wpilib import XboxController

from abc import ABC, abstractmethod


class _InputManager(ABC):
    """
    Abstract base class holding necessary methods for
    input managers.
    """

    @abstractmethod
    def __register(self, input_type, condition, action):
        pass


class Button(XboxController.Button):
    """
    Xbox controller buttons.
    """


class Axis(XboxController.Axis):
    """
    Xbox controller axis.
    """


class ButtonEvent(Enum):
    """
    Supported button events.
    """

    kOnPress = auto()
    kOnRelease = auto()
    kWhilePressed = auto()
    kWhileReleased = auto()


# HACK emulate enum values in methods
#      to take arguments.
class AxisEvent:

    @staticmethod
    def kLessThan(value):
        return value

    @staticmethod
    def kGreaterThan(value):
        return value

    @staticmethod
    def kAtValue(value):
        return value


class AxisManager(_InputManager):

    def __init__(self, controller):
        pass

    def __register(self, axis, condition, action):
        pass

    def __enter__(self):
        return self.__register

    def __exit__(self, *err_args):
        pass


class ButtonManager(_InputManager):

    def __init__(self, controller):
        pass

    def __register(self, button, condition, action):
        pass

    def __enter__(self):
        return self.__register

    def __exit__(self, *err_args):
        pass


class InputManager(_InputManager):

    def __init__(self, controller):
        pass

    def __register(self, input_type, condition, action):
        pass

    def __enter__(self):
        return self.__register

    def __exit__(self, *err_args):
        pass
