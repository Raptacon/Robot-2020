# General imports
import wpilib
from magicbot import MagicRobot

# Component imports
# No components yet, we need to rebuild them

# Other imports
from utils.configutil import InitializeRobot


class MyRobot(MagicRobot):
    """
    Base robot class of Magic Bot Type
    """

    # Components
    # Again, none yet. We need to rebuild
    # the components for this years robot(s).

    # def init(self):
    #     print("it worked")

    # # create a more syntactically sound name for `createObjects`
    # # by altering namespace:
    # createObjects = init

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit

        XXX The name `createObjects` is a bit deceptive, because this
        does more than just "create objects" for the robot. It initializes
        the robot in many different ways (functions as the `__init__`).
        """

        InitializeRobot(self, default_cfg="doof.json")

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        ...


if __name__ == '__main__':
    wpilib.run(MyRobot)
