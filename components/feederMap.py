from wpilib import XboxController
from components.controllerManager import XboxControllers, AxisManager
from components.shooterMotors import ShooterMotorCreation, Direction
from enum import Enum, auto
from magicbot import tunable
import logging

class Type(Enum):
    """Enumeration for the two types within the feeder."""
    kIntake = auto()
    kLoader = auto()

class FeederMap:
    """Simple map that holds the logic for running elements of the feeder."""

    compatString = ["doof"]

    shooterMotors: ShooterMotorCreation
    # xboxMap: XboxMap
    axisManager: AxisManager
    logger: logging

    loaderMotorSpeed = tunable(.4)
    intakeMotorSpeed = tunable(.7)

    def on_enable(self):
        pass
        # self.logger.setLevel(logging.DEBUG)

    def run(self, loaderFunc):
        """Called when execution of a feeder element is desired."""
        if loaderFunc == Type.kIntake:
            forwardIntakeValue = self.axisManager.getBoundAxis(XboxControllers.kMech, XboxController.Axis.kRightTrigger, .6, .8)
            backwardsIntakeValue = self.axisManager.getBoundAxis(XboxControllers.kMech, XboxController.Axis.kLeftTrigger, .6, .8)
            self.shooterMotors.runIntake(forwardIntakeValue, Direction.kForwards)
            self.shooterMotors.runIntake(backwardsIntakeValue, Direction.kBackwards)

        if loaderFunc == Type.kLoader:
            forwardLoaderValue = self.axisManager.getBoundAxis(XboxControllers.kMech, XboxController.Axis.kRightTrigger, .4, .4)
            backwardsLoaderValue = self.axisManager.getBoundAxis(XboxControllers.kMech, XboxController.Axis.kLeftTrigger, .4, .4)
            self.shooterMotors.runLoader(forwardLoaderValue, Direction.kForwards)
            self.shooterMotors.runLoader(backwardsLoaderValue, Direction.kBackwards)

    def execute(self):
        pass
