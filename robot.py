# General imports
import wpilib
from magicbot import MagicRobot

# Component imports
# No components yet, we need to rebuild them

# Other imports
from utils.configutil import InitializeRobot, parse_robot_args


class MyRobot(MagicRobot):
    """
    Base robot class of Magic Bot Type
    """

    # Components
    # Again, none yet. We need to rebuild
    # the components for this years robot(s).

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit
        """

        InitializeRobot(self, default_config="doof.json")

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        ...


if __name__ == '__main__':
    parse_robot_args()
    wpilib.run(MyRobot)
