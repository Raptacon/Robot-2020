from magicbot import MagicRobot

from components.component1 import Component1

from utils.hardware.hardware_manager import generate_hardware_objects


class MyDoof(MagicRobot):

    component1: Component1

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        pass
