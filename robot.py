# General imports:
import wpilib
from magicbot import MagicRobot

# Component imports:
# No components yet, we need to rebuild them

# Other imports
from utils.configmanager import InitializeRobot


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

        InitializeRobot(self, cfg_file="doof.json", generate_objects=False)

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        ...


if __name__ == '__main__':
    wpilib.run(MyRobot)
