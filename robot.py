# General imports
import wpilib
from magicbot import MagicRobot

# Component imports
# No components yet, we need to rebuild them

# Other imports
from utils.configutil import ConfigManager
from utils.hardwareutil import generate_hardware_objects
from utils.robotutil import cleanup_components

def dummyregsiter(objects: list=None):
    pass

class MyRobot(MagicRobot):
    """
    Base robot class of Magic Bot Type
    """

    # Components
    # Again, none yet. We need to rebuild
    # the components for this years robot(s).

    def createObjects(self):
        """
        Robot-wide initialization.

        XXX The name `createObjects` is a bit deceptive, because this
        does more than just "create objects" for the robot. It initializes
        the robot in many different ways (functions as the `__init__`).
        """

        config = ConfigManager(self, default="doof.json")
        generate_hardware_objects(self, hardware_cfg=config.data)
        cleanup_components(self, key=config.name)

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """

        ...


if __name__ == '__main__':
    wpilib.run(MyRobot)
