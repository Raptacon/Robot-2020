"""
Class that uses inputs, particularly from the limelight,
to align the bot to a target
"""
from components.driveTrain import DriveTrain
from components.limelight import Limelight, LimelightCamMode, LimelightLightMode
from enum import Enum, auto
import logging

class AlignStates(auto):
    kNone = auto()
    kAligningX = auto()
    kAliginingY = auto()
    kAliginingXY = auto()

class Align():
    drivetrain: DriveTrain

    def setup(self):
        self.currentAligningState = AlignStates.kNone

    def alignToX(self):
        self.currentAligningState = AlignStates.kAligningX

    def alignToY(self):
        self.currentAligningState = AlignStates.kAliginingY

    def aliginToXY(self):
        self.currentAligningState = AlignStates.kAliginingXY

    def execute(self):
        try:
            xoffset = Limelight.getXOffset()
        except AssertionError as error:
            logging.error("Alignment failed due to error: %s"% error)

        if self.currentAligningState == AlignStates.kAligningX:
            self.drivetrain.setArcade(0, xoffset)
        elif self.currentAligningState == AlignStates.kAliginingXY:
            self.drivetrain.setArcade(0, xoffset)
            logging.info("Aligning to Y not yet implemented, skipping")
        elif self.currentAligningState == AlignStates.kAliginingY:
            logging.info("Aligning to Y not yet implemented, skipping")