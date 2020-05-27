from robotMap import XboxMap
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
    #xboxMap: XboxMap
    logger: logging

    controllers: dict

    loaderMotorSpeed = tunable(.4)
    intakeMotorSpeed = tunable(.7)

    def on_enable(self):

        self.mech = self.controllers['mech']

        self.logger.setLevel(logging.DEBUG)

    def run(self, loaderFunc):
        """Called when execution of a feeder element is desired."""
        if loaderFunc == Type.kIntake:
            if self.mech.rightTrigger > 0 and self.mech.leftTrigger == 0:
                self.shooterMotors.runIntake(self.intakeMotorSpeed, Direction.kForwards)
                self.logger.debug(f"right trig intake {self.mech.rightTrigger}")

            elif self.mech.leftTrigger > 0 and self.mech.rightTrigger == 0:
                self.shooterMotors.runIntake(self.intakeMotorSpeed, Direction.kBackwards)
                self.logger.debug(f"left trig intake {self.mech.leftTrigger}")

            else:
                self.shooterMotors.stopIntake()

        if loaderFunc == Type.kLoader:
            if self.mech.rightTrigger > 0 and self.mech.leftTrigger == 0:
                self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)
                self.logger.debug(f"right trig manual {self.mech.rightTrigger}")

            elif self.mech.leftTrigger > 0 and self.mech.rightTrigger == 0:
                self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kBackwards)
                self.logger.debug(f"left trig manual {self.mech.leftTrigger}")

            else:
                self.shooterMotors.stopLoader()

    def execute(self):
        pass
