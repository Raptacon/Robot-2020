from wpilib import run
from magicbot import MagicRobot

from .components.component1 import Component1


class RobotDoof(MagicRobot):

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic for doof')

if __name__ == '__main__':
    run(RobotDoof)
