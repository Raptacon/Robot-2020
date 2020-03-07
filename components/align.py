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
    driveTrain: DriveTrain
    limelight: Limelight

    def setup(self):
        self.currentAligningState = AlignStates.kNone

    def alignToX(self):
        self.currentAligningState = AlignStates.kAligningX

    def alignToY(self):
        self.currentAligningState = AlignStates.kAliginingY

    def aliginToXY(self):
        self.currentAligningState = AlignStates.kAliginingXY

    def stopAlign(self):
        self.currentAligningState = AlignStates.kNone

    def execute(self):
        if self.currentAligningState != AlignStates.kNone:
            self.limelight.setLEDMode(LimelightLightMode.kOn)
            self.limelight.setCameraMode(LimelightCamMode.kProcessingMode)
            try:
                xoffset = self.limelight.getXOffset()
            except AssertionError as error:
                logging.error("Alignment failed due to error: %s"% error)
                self.stopAlign()

        if self.currentAligningState == AlignStates.kAligningX:
            self.driveTrain.setArcade(0, xoffset)
        elif self.currentAligningState == AlignStates.kAliginingXY:
            self.driveTrain.setArcade(0, xoffset)
            logging.info("Aligning to Y not yet implemented, skipping")
        elif self.currentAligningState == AlignStates.kAliginingY:
            logging.info("Aligning to Y not yet implemented, skipping")

        if self.currentAligningState != AlignStates.kNone:
            self.limelight.setLEDMode(LimelightLightMode.kOff)
            self.limelight.setCameraMode(LimelightCamMode.kDriverMode)