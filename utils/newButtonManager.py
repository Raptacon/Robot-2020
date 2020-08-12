from threading import Thread
from wpilib import XboxController
from enum import Flag, auto
from importlib import import_module
from time import sleep
import traceback
from utils.filehandler import FileHandler
from inspect import getargspec


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
        
        assert button_config is not None, "Must specify a button config file."

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
                        controller = getattr(robot, 'controllers')[event['controller']].controller
                        button = eval(event['button'])
                        condition = eval('ButtonEvent.' + event['condition'])
                        module = import_module(event['action']['module'])
                        comp = getattr(module, event['action']['component'])
                        action = getattr(comp, event['action']['func'])
                    except:
                        print(f"A button event crashed.\nEvent: {event}")
                        traceback.print_exc()

                    event_mappings[condition](controller, button, action)

        updater = Thread(target=update)
        updater.start()

    def __process_event(self, action):
        args, _, _, _ = getargspec(action)
        action()

    def __run_OnPress(self, controller, button, action):
        """
        Run button event when button is pressed.
        """

        wasButtonPressed = controller.getRawButtonPressed(button)
        if wasButtonPressed:
            self.__process_event(action)

    def __run_OnRelease(self, controller, button, action):
        """
        Run button event when button is released.
        """

        wasButtonReleased = controller.getRawButtonReleased(button)
        if wasButtonReleased:
            self.__process_event(action)

    def __run_WhilePressed(self, controller, button, action):
        """
        Run button event while button is pressed.
        """

        isButtonPressed = controller.getRawButton(button)
        if isButtonPressed:
            self.__process_event(action)

    def __run_WhileReleased(self, controller, button, action):
        """
        Run button event while button is released.
        """

        isButtonReleased = not controller.getRawButton(button)
        if isButtonReleased:
            self.__process_event(action)