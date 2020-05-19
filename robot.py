"""
Team 3200 Robot base class
"""
# Module imports:
import wpilib
from wpilib import XboxController
from magicbot import MagicRobot, tunable

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
from robotMap import XboxMap
from utils.componentUtils import createComponents
from utils.reworkedConfig import ConfigurationManager
import utils.math

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

    sensitivityExponent = tunable(1.8)

    def createObjects(self):
        """
        Robot-wide initialization code should go here. Replaces robotInit
        """

        self.mapper = ConfigurationManager(self)
        self.xboxMap = XboxMap(XboxController(1), XboxController(0))
        createComponents(self)

    def autonomousInit(self):
        """Run when autonomous is enabled."""
        self.shooter.autonomousEnabled()
        self.loader.stopLoading()

    def teleopInit(self):
        # Register button events for doof
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kX, ButtonEvent.kOnPress, self.pneumatics.toggleLoader)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kY, ButtonEvent.kOnPress, self.loader.setAutoLoading)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kB, ButtonEvent.kOnPress, self.loader.setManualLoading)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kA, ButtonEvent.kOnPress, self.shooter.shootBalls)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kA, ButtonEvent.kOnPress, self.loader.stopLoading)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kA, ButtonEvent.kOnRelease, self.shooter.doneShooting)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kA, ButtonEvent.kOnRelease, self.loader.determineNextAction)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kBumperRight, ButtonEvent.kOnPress, self.elevator.setRaise)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kBumperRight, ButtonEvent.kOnRelease, self.elevator.stop)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kBumperLeft, ButtonEvent.kOnPress, self.elevator.setLower)
        self.buttonManager.registerButtonEvent(self.xboxMap.mech, XboxController.Button.kBumperLeft, ButtonEvent.kOnRelease, self.elevator.stop)
        self.buttonManager.registerButtonEvent(self.xboxMap.drive, XboxController.Button.kBumperLeft, ButtonEvent.kOnPress, self.driveTrain.enableCreeperMode)
        self.buttonManager.registerButtonEvent(self.xboxMap.drive, XboxController.Button.kBumperLeft, ButtonEvent.kOnRelease, self.driveTrain.disableCreeperMode)

        self.shooter.autonomousDisabled()

    def teleopPeriodic(self):
        """
        Must include. Called running teleop.
        """
        self.xboxMap.controllerInput()

        driveLeft = utils.math.expScale(self.xboxMap.getDriveLeft(), self.sensitivityExponent) * self.driveTrain.driveMotorsMultiplier
        driveRight = utils.math.expScale(self.xboxMap.getDriveRight(), self.sensitivityExponent) * self.driveTrain.driveMotorsMultiplier

        self.driveTrain.setTank(driveLeft, driveRight)

        if self.xboxMap.getMechDPad() == 0:
            self.winch.setRaise()
        else:
            self.winch.stop()

        self.scorpionLoader.checkController()

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
