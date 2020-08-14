from threading import Thread
from wpilib import XboxController
from enum import Flag, auto
from importlib import import_module
from time import sleep
import traceback
from utils.filehandler import FileHandler
from inspect import getargspec
from typing import get_type_hints


BUTTON_UPDATE_DELAY = 0.020


class ButtonEvent(Flag):
    """
    Supported button actions
    """
    kOnPress = auto()
    kOnRelease = auto()
    kWhilePressed = auto()
    kWhileReleased = auto()
    kNone = 0


class ButtonSetup(FileHandler):

    def __init__(self, robot, button_config=None):
        
        assert button_config is not None, (
            "Must specify a button config file."
        )

        button_data = self.load(button_config)

        event_mappings = {
            ButtonEvent.kOnPress: self.__run_OnPress,
            ButtonEvent.kOnRelease: self.__run_OnRelease,
            ButtonEvent.kWhilePressed: self.__run_WhilePressed,
            ButtonEvent.kWhileReleased: self.__run_WhileReleased
        }

        
        def update():

            while True:

                sleep(BUTTON_UPDATE_DELAY)

                for event in button_data:

                    try:
                        _controllers = getattr(robot, 'controllers')
                        _controller_name = event['controller']
                        controller = _controllers[_controller_name].controller
                        button = eval(event['button'])
                        condition = eval('ButtonEvent.' + event['condition'])
                        _component = event['action']['component']
                        _func = event['action']['func']
                        _components = get_type_hints(robot)
                        component = _components[_component]
                        func = getattr(component, _func)
                    except:
                        print(f"A button event crashed.\nEvent: {event}")
                        traceback.print_exc()

                    event_mappings[condition](controller, button, func)

        updater = Thread(target=update)
        updater.start()

    def __run_OnPress(self, controller, button, action):
        """
        Run button event when button is pressed.
        """

        wasButtonPressed = controller.getRawButtonPressed(button)
        if wasButtonPressed:
            action()

    def __run_OnRelease(self, controller, button, action):
        """
        Run button event when button is released.
        """

        wasButtonReleased = controller.getRawButtonReleased(button)
        if wasButtonReleased:
            action()

    def __run_WhilePressed(self, controller, button, action):
        """
        Run button event while button is pressed.
        """

        isButtonPressed = controller.getRawButton(button)
        if isButtonPressed:
            action()

    def __run_WhileReleased(self, controller, button, action):
        """
        Run button event while button is released.
        """

        isButtonReleased = not controller.getRawButton(button)
        if isButtonReleased:
            action()