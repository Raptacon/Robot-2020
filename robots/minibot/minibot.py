from wpilib import run
from magicbot import MagicRobot


class RobotMinibot(MagicRobot):

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic for minibot')

if __name__ == '__main__':
    run(RobotMinibot)