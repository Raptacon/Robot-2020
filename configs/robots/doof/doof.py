from wpilib import run
from magicbot import MagicRobot


class RobotDoof(MagicRobot):

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic for doof')

if __name__ == '__main__':
    run(RobotDoof)
