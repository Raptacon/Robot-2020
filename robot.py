# General imports:
import wpilib
from magicbot import MagicRobot

# Component imports:
from components.driveTrain import DriveTrain
from components.pneumatics import Pneumatics
from components.breakSensors import Sensors
from components.winch import Winch
from components.shooterMotors import ShooterMotorCreation
from components.shooterLogic import ShooterLogic
from components.loaderLogic import LoaderLogic
from components.elevator import Elevator
# from components.scorpionLoader import ScorpionLoader
from components.feederMap import FeederMap

# Other imports
from utils.configmanager import InitializeRobot
from utils.buttonmanager import ButtonManager, Button, ButtonEvent
from warnings import warn


class MyRobot(MagicRobot):
    """
    Base robot class of Magic Bot Type
    """

    shooter: ShooterLogic
    loader: LoaderLogic
    feeder: FeederMap
    sensors: Sensors
    shooterMotors: ShooterMotorCreation
    driveTrain: DriveTrain
    winch: Winch
    pneumatics: Pneumatics
    elevator: Elevator

    inputs_XboxControllers: dict
    motors_driveTrain:      dict
    motors_loader:          dict
    motors_shooter:         dict
    motors_elevator:        dict
    motors_winch:           dict
    sensors_breaksensors:   dict
    pneumatics_compressors: dict
    pneumatics_solenoids:   dict


    # HACK classmethod necessary to access
    #  __dict__ from class rather than instance
    @classmethod
    def __component_cleanup(cls, config):
        """
        Remove incompatable components from the robot class.
        """

        #
        # NOTE: `_builtin_types` assures that injectable types
        #       aren't removed or checked for a `robot` attribute,
        #       but injectables SHOULD NOT be used in MyRobot.
        #

        _builtin_types = ('str', 'int', 'float', 'complex', 'list',
                          'tuple', 'range', 'dict', 'set', 'frozenset',
                          'bool', 'bytes', 'bytearray', 'memoryview',)
        annotations = cls.__dict__.get("__annotations__")
        bad_components = []

        for cname, c in annotations.items():
            if not c.__name__ in _builtin_types:
                compat_robots = getattr(c, "robot", None)
                if not compat_robots:

                    #
                    # XXX: Should this be a warning and enable the
                    #      component by default?
                    #
                    #      Or, we could seperate robot components into their
                    #      own directories (i.e. components\doof\component.py)
                    #      and use inspect.getsourcefile(c) to check if the
                    #      component belongs to a specific robot (then no need
                    #      for a `robot` attribute at all).
                    #

                    raise AttributeError(
                        f"Component {cname} ({c}) is missing a 'robot'"
                        " attribute; component cannot be created."
                    )
                if config in compat_robots or "all" in compat_robots:
                    continue
                else:
                    bad_components.append(cname)

        for bad_comp in bad_components:
            del annotations[bad_comp]

    def __check_controllers(self, needed_inputs):
        """
        Checks the number of controllers needed to register
        input events with a robot against the actual number
        of controllers found.
        """

        if len(self.inputs_XboxControllers) != needed_inputs:
            raise ValueError("")

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit
        """

        self.initializer = InitializeRobot(self)
        self.__component_cleanup(self.initializer.config)

    def autonomousInit(self):
        """Run when autonomous is enabled."""
        self.shooter.autonomousEnabled()
        self.loader.stopLoading()

    def teleopInit(self):

        self.shooter.autonomousDisabled()

        #
        # TODO: figure out how to support button events for other robots.
        #       Right now this is exclusive to doof.
        #
        # XXX: Should we handle buttons within individual components?
        #      We could register buttons in the `on_enable` portion of
        #      the components. This would allow buttons to be used on
        #      different robots because when the components are disabled,
        #      the button events won't be registered.
        #
        #      Or, we could have a buttons component that handles
        #      button registration in the `on_enable` portion and
        #      updates the axis in the `execute` portion. This
        #      would eliminate the need to use threads to update
        #      controllers.
        #
        # XXX: Injectables shouldn't be used in MyRobot. They are
        #      designed for components.
        #

        # Setup button events

        if self.initializer.config != "doof":
            warn(
                f"Robot '{self.initializer.config}' doesn't support buttons.",
                Warning
            )
            return

        drive_controller = self.inputs_XboxControllers["drive"].controller
        mech_controller = self.inputs_XboxControllers["mech"].controller

        with ButtonManager(drive_controller) as drive_events:
            drive_events(Button.kBumperLeft, ButtonEvent.kOnPress, self.driveTrain.enableCreeperMode)
            drive_events(Button.kBumperLeft, ButtonEvent.kOnRelease, self.driveTrain.disableCreeperMode)

        with ButtonManager(mech_controller) as mech_events:
            mech_events(Button.kX, ButtonEvent.kOnPress, self.pneumatics.toggleLoader)
            mech_events(Button.kY, ButtonEvent.kOnPress, self.loader.setAutoLoading)
            mech_events(Button.kB, ButtonEvent.kOnPress, self.loader.setManualLoading)
            mech_events(Button.kA, ButtonEvent.kOnPress, self.shooter.shootBalls)
            mech_events(Button.kA, ButtonEvent.kOnPress, self.loader.stopLoading)
            mech_events(Button.kA, ButtonEvent.kOnRelease, self.shooter.doneShooting)
            mech_events(Button.kA, ButtonEvent.kOnRelease, self.loader.determineNextAction)
            mech_events(Button.kBumperRight, ButtonEvent.kOnPress, self.elevator.setRaise)
            mech_events(Button.kBumperRight, ButtonEvent.kOnRelease, self.elevator.stop)
            mech_events(Button.kBumperLeft, ButtonEvent.kOnPress, self.elevator.setLower)
            mech_events(Button.kBumperLeft, ButtonEvent.kOnRelease, self.elevator.stop)

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        pass

if __name__ == '__main__':
    import sys

    wpilib.run(MyRobot)
