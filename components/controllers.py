from wpilib import XboxController
from enum import Enum, auto


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
