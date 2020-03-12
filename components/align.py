"""
Class that uses inputs, particularly from the limelight,
to align the bot to a target
"""
from components.driveTrain import DriveTrain
from components.limelight import Limelight, LimelightCamMode, LimelightLightMode
from enum import auto
import logging

class AlignStates(auto):
    """
    class for holding enums for
    the different alignemnt modes
    """
    kNone = auto()
    kAligningX = auto()
    kAliginingY = auto()
    kAliginingXY = auto()

class Align():
    """
    Class for aligining the robot
    using drivetrain
    """
    driveTrain: DriveTrain
    limelight: Limelight

    def setup(self):
        """
        this code runs after injection, instead of init
        """
        self.currentAligningState = AlignStates.kNone

    def alignToX(self):
        """
        Set the mode so that execute knows that
        we want to align on the x axis
        """
        self.currentAligningState = AlignStates.kAligningX

    def alignToY(self):
        """
        Set the mode so that execute knows that
        we want to align on the y axis. This
        has not been implemented
        """
        self.currentAligningState = AlignStates.kAliginingY

    def aliginToXY(self):
        """
        Set the mode so that execute knows that
        we want to align on the x and y axis. This
        has not been implemented
        """
        self.currentAligningState = AlignStates.kAliginingXY

    def stopAlign(self):
        """
        Set the mode so that execute knows that
        we are done aligning.
        """
        self.currentAligningState = AlignStates.kNone

    def execute(self):
        """
        runs every time periodic is called
        """
        if self.currentAligningState != AlignStates.kNone:
            self.limelight.setLEDMode(LimelightLightMode.kOn)
            self.limelight.setCameraMode(LimelightCamMode.kProcessingMode)
            try:
                xoffset = self.limelight.getXOffset()
            except AssertionError as error:
                logging.error("Alignment failed due to error: %s"% error)
                self.stopAlign()

        if self.currentAligningState == AlignStates.kAligningX:
            self.driveTrain.autoTracking(-0.05, xoffset)
        elif self.currentAligningState == AlignStates.kAliginingXY:
            self.driveTrain.autoTracking(-0.05, xoffset)
            logging.info("Aligning to Y not yet implemented, skipping")
        elif self.currentAligningState == AlignStates.kAliginingY:
            logging.info("Aligning to Y not yet implemented, skipping")

        if self.currentAligningState == AlignStates.kNone:
            self.limelight.setLEDMode(LimelightLightMode.kOff)
            self.limelight.setCameraMode(LimelightCamMode.kDriverMode)
