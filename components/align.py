"""
Class that uses inputs, particularly from the limelight,
to align the bot to a target
"""
from components.driveTrain import DriveTrain
from components.limelight import Limelight, LimelightCamMode, LimelightLightMode
from enum import Enum, auto

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
        """if self.currentAligningState == AlignStates.ali
            offset = Limelight.getXOffset()
            self.drivetrain.setArcade(0, offset)"""