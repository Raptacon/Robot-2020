from wpilib import run
from magicbot import MagicRobot

from .components.component1 import Component1

from factories.actuator import GenerateObjects


class RobotDoof(MagicRobot):

    #component1: Component1

    def createObjects(self):
        GenerateObjects(self, config_name='doof_config.json')

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic for doof')

if __name__ == '__main__':
    run(RobotDoof)
