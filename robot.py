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
from components.feederMap import FeederMap

# Other imports
from utils.configmanager import InitializeRobot
from utils.buttonmanager import ButtonManager, Button, ButtonEvent
from warnings import warn
from typing import List, Tuple


class MyRobot(MagicRobot):
    """
    Base robot class of Magic Bot Type
    """

    # Components
    shooter: ShooterLogic
    loader: LoaderLogic
    feeder: FeederMap
    sensors: Sensors
    shooterMotors: ShooterMotorCreation
    driveTrain: DriveTrain
    winch: Winch
    pneumatics: Pneumatics
    elevator: Elevator

    # Controllers
    inputs_XboxControllers: dict

    # TODO: remove `__component_cleanup` if we
    #       don't use multiple robots.

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
        #       but injectables SHOULD NOT be used in MyRobot
        #       (with the exception of inputs_XboxControllers,
        #       they are used for buttons).
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
            cls.logger.info(f"Removing component {bad_comp}")
            del annotations[bad_comp]

    def __register_buttons(self, controller, events: List[Tuple[Button, ButtonEvent, callable]]=None):

        with ButtonManager(controller) as register:
            for event in events:
                register(event)

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit
        """

        i = InitializeRobot(self)
        # Attr set to avoid making `i` and instance
        # variable just to access the `config` attribute
        setattr(self, "robot_name", i.config)
        self.__component_cleanup(self.robot_name)

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
        #       NOTE: This will likely need to be "brute-forced"
        #             (chain of if-elif statements) because buttons
        #             can't live in a config file and they have
        #             to be explicitly listed here.
        #
        #             If we decide NOT to use multiple robots,
        #             this won't be necessary.
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

        if self.robot_name == "doof":

            drive_controller = self.inputs_XboxControllers["drive"].controller
            mech_controller = self.inputs_XboxControllers["mech"].controller

            self.__register_buttons(drive_controller, events=[
                (Button.kBumperLeft,    ButtonEvent.kOnPress,   self.driveTrain.enableCreeperMode   ),
                (Button.kBumperLeft,    ButtonEvent.kOnRelease, self.driveTrain.disableCreeperMode  )
            ])

            self.__register_buttons(mech_controller, events=[
                (Button.kX,             ButtonEvent.kOnPress,   self.pneumatics.toggleLoader        ),
                (Button.kY,             ButtonEvent.kOnPress,   self.loader.setAutoLoading          ),
                (Button.kB,             ButtonEvent.kOnPress,   self.loader.setManualLoading        ),
                (Button.kA,             ButtonEvent.kOnPress,   self.loader.stopLoading             ),
                (Button.kA,             ButtonEvent.kOnPress,   self.shooter.shootBalls             ),
                (Button.kA,             ButtonEvent.kOnRelease, self.shooter.doneShooting           ),
                (Button.kA,             ButtonEvent.kOnRelease, self.loader.determineNextAction     ),
                (Button.kBumperRight,   ButtonEvent.kOnPress,   self.elevator.setRaise              ),
                (Button.kBumperRight,   ButtonEvent.kOnRelease, self.elevator.stop                  ),
                (Button.kBumperLeft,    ButtonEvent.kOnPress,   self.elevator.setLower              ),
                (Button.kBumperLeft,    ButtonEvent.kOnRelease, self.elevator.stop                  )
            ])

        elif self.robot_name == "scorpion":
            warn(f"Robot '{self.robot_name}' has no button events.", Warning)

        elif self.robot_name == "minibot":
            warn(f"Robot '{self.robot_name}' has no button events.", Warning)

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        ButtonManager.update_buttons()

if __name__ == '__main__':
    wpilib.run(MyRobot)
