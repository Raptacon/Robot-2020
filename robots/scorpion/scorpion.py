from wpilib import run
from magicbot import MagicRobot


class RobotScorpion(MagicRobot):

    def createObjects(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print('teleop periodic for scorpion')

if __name__ == '__main__':
    run(RobotScorpion)