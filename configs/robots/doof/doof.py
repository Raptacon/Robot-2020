from wpilib import run
from magicbot import MagicRobot

import importlib
import os


class RobotDoof(MagicRobot):

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic')

if __name__ == '__main__':
    run(RobotDoof)
