"""
Team 3200 Robot base class
"""
# Module imports:
import wpilib
from wpilib import XboxController
from magicbot import MagicRobot

# Component imports:
from components.driveTrain import DriveTrain
from components.pneumatics import Pneumatics
from components.buttonManager import ButtonManager, ButtonEvent
from components.breakSensors import Sensors
from components.winch import Winch
from components.shooterMotors import ShooterMotorCreation
from components.shooterLogic import ShooterLogic
from components.loaderLogic import LoaderLogic
from components.elevator import Elevator
from components.scorpionLoader import ScorpionLoader
from components.feederMap import FeederMap

# Other imports:
from utils.reworkedConfig import InitializeRobot


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
    buttonManager: ButtonManager
    pneumatics: Pneumatics
    elevator: Elevator
    scorpionLoader: ScorpionLoader

    controllers: dict

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit
        """

        InitializeRobot(self)

    def autonomousInit(self):
        """Run when autonomous is enabled."""
        self.shooter.autonomousEnabled()
        self.loader.stopLoading()

    def teleopInit(self):
        # Register button events for doof
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kX, ButtonEvent.kOnPress, self.pneumatics.toggleLoader)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kY, ButtonEvent.kOnPress, self.loader.setAutoLoading)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kB, ButtonEvent.kOnPress, self.loader.setManualLoading)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kA, ButtonEvent.kOnPress, self.shooter.shootBalls)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kA, ButtonEvent.kOnPress, self.loader.stopLoading)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kA, ButtonEvent.kOnRelease, self.shooter.doneShooting)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kA, ButtonEvent.kOnRelease, self.loader.determineNextAction)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kBumperRight, ButtonEvent.kOnPress, self.elevator.setRaise)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kBumperRight, ButtonEvent.kOnRelease, self.elevator.stop)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kBumperLeft, ButtonEvent.kOnPress, self.elevator.setLower)
        self.buttonManager.registerButtonEvent(self.controllers['mech'].controller, XboxController.Button.kBumperLeft, ButtonEvent.kOnRelease, self.elevator.stop)
        self.buttonManager.registerButtonEvent(self.controllers['drive'].controller, XboxController.Button.kBumperLeft, ButtonEvent.kOnPress, self.driveTrain.enableCreeperMode)
        self.buttonManager.registerButtonEvent(self.controllers['drive'].controller, XboxController.Button.kBumperLeft, ButtonEvent.kOnRelease, self.driveTrain.disableCreeperMode)

        self.shooter.autonomousDisabled()

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        pass

    def testInit(self):
        """
        Function called when testInit is called.
        """
        print("testInit was Successful")

    def testPeriodic(self):
        """
        Called during test mode alot
        """
        pass

if __name__ == '__main__':
    wpilib.run(MyRobot)
