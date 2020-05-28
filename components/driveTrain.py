import wpilib.drive
from enum import Enum, auto
from magicbot import tunable


class ControlMode(Enum):
    """
    Drive Train Control Modes
    """
    kArcadeDrive = auto()
    kTankDrive = auto()
    kAngleTurning = auto()
    kDisabled = auto()

class DriveTrain():
    # Note - The way we will want to do this will be to give this component motor description dictionaries from robotmap and then creating the motors with motorhelper. After that, we simply call wpilib' differential drive
    motors_driveTrain: dict
    controllers: dict
    driveMotorsMultiplier = tunable(.5)
    sensitivityExponent = tunable(1.8)
    #gyros_system: dict

    compatString = ["all"]

    def setup(self):
        self.tankLeftSpeed = 0
        self.tankRightSpeed = 0
        self.arcadeSpeed = 0
        self.arcadeRotation = 0
        self.creeperMode = False
        self.controlMode = ControlMode.kDisabled
        self.leftMotor = self.motors_driveTrain["leftMotor"]
        self.rightMotor = self.motors_driveTrain["rightMotor"]
        self.drive = self.controllers['drive']
        self.driveTrain = wpilib.drive.DifferentialDrive(self.leftMotor, self.rightMotor)
        self.logger.info("DriveTrain setup completed")

    def expScale(self, initVal, exp):
        """
        Applies an exponent exp to a value initVal and returns value.
        Will work whether initVal is positive or negative or zero.
        """

        val = initVal
        if val > 0:
            val = val ** exp
        if val < 0:
            val *= -1
            val = val ** exp
            val *= -1
        return val

    def getLeft(self):
        return self.leftMotor.get()

    def getRight(self):
        return self.rightMotor.get()

    def isStopping(self):
        pass

    def setTank(self, leftSpeed, rightSpeed):
        self.controlMode = ControlMode.kTankDrive
        self.tankLeftSpeed = leftSpeed
        self.tankRightSpeed = rightSpeed

    def setArcade(self, speed, rotation):
        self.controlMode = ControlMode.kArcadeDrive
        self.arcadeSpeed = speed
        self.arcadeRotation = rotation

    def enableCreeperMode(self):
        """when left bumper is pressed, it sets the driveMotorsMultiplier to .25"""
        if self.creeperMode:
            return
        self.prevMultiplier = self.driveMotorsMultiplier
        self.driveMotorsMultiplier = .25
        self.creeperMode = True

    def disableCreeperMode(self):
        """when left bumper is released, it sets the multiplier back to it's original value"""
        if not self.creeperMode:
            return
        self.driveMotorsMultiplier = self.prevMultiplier
        self.creeperMode = False

    def stop(self, coast=False):
        self.controlMode = ControlMode.kDisabled

    def getMeasuredSpeed(self):
        pass

    def execute(self):

        driveLeft = self.expScale(self.drive.leftY, self.sensitivityExponent) * self.driveMotorsMultiplier
        driveRight = self.expScale(self.drive.rightY, self.sensitivityExponent) * self.driveMotorsMultiplier

        self.setTank(driveLeft, driveRight)

        if self.controlMode == ControlMode.kTankDrive:
            self.driveTrain.tankDrive(self.tankLeftSpeed, self.tankRightSpeed, False)

        elif self.controlMode == ControlMode.kArcadeDrive:
            self.driveTrain.arcadeDrive(self.arcadeSpeed, self.arcadeRotation, False)
