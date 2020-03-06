"""
Manager to more easily read the values
from the limelight and more easily write
to for pipeline changes
"""
from networktables import NetworkTables
from enum import Enum

class LimelightCamMode(Enum):
    """
    Limelight defined camera modes that
    can be set through the network tables.
    kDriverMode provides a human useable view,
    kProcessingMode is for computer processing
    """
    kDriverMode = 1
    kProcessingMode = 0

class LimelightLightMode(Enum):
    """
    limelight defined light modes that can
    be set through the network tables
    """
    kDefault = 0
    kOff = 1
    kBlink = 2
    kOn = 3
    

class Limelight:
    """
    Class for access and assignment of values.
    This is a low level component
    """

    def setup(self):
        """
        Sets up the limelight access. Since it is
        a "plug and play" device, there is no need
        for any actual component creation
        """
        self.limelightTable = NetworkTables.getTable("limelight")
        self.setCameraMode(LimelightCamMode.kDriverMode)
        self.setLEDMode(LimelightLightMode.kOff)

    def _checkForObject(self):
        """
        throws an error if there is not an object
        in view. This leaves it up to the calling
        object on what to do.
        """
        assert self.limelightTable.getNumber("tv") == 1, "there is no object in view, cannot get offset" #this is pretty weird for me - just let me know or fix it if it is overkill

    def getXOffset(self):
        """
        gets, from the network tables, how far off, in the
        horizontal direction, the crosshair is from the sensed 
        targed. throws an error if there is no target in view
        """
        self._checkForObject(self)
        return self.limelightTable.getNumber("tx")

    def getYOffset(self):
        """
        gets, from the network tables, how far off, in the
        vertical direction, the crosshair is from the sensed
        targed. throws an error if there is no target in view
        """
        self._checkForObject(self)
        return self.limelightTable.getNumber("ty")

    def getSize(self):
        """
        returns the area of a sensed target, from 0 to 100.
        This is a percent of the image.
        """
        self._checkForObject(self)
        return self.limelightTable.getNumber("ta")

    def setPipeline(self, pipeline: int):
        """
        Sets the pipeline for the limelight to target.
        returns the previous pipeline
        """
        prevPipeline = self.limelightTable.getNumber("pipeline")
        self.limelightTable.putNumber("pipeline", pipeline)
        return prevPipeline

    def setCameraMode(self, mode: LimelightCamMode):
        """
        set the limelight to either driver mode or
        processing mode, using the enumerated class
        return the previous mode
        """
        prevMode = self.limelightTable.getNumber("camMode", 0)
        self.limelightTable.putNumber("camMode", mode)#FIXME enum to float fix
        return prevMode

    def setLEDMode(self, mode: LimelightLightMode):
        """
        sets the limelight led to one of the enumerated values from
        class LimelightLightMode. Make sure to use sparingly
        returns the previous mode
        """
        prevLED = self.limelightTable.getNumber('ledMode')
        self.limelightTable.putNumber("ledMode", mode)
        return prevLED

    def limelightOff(self):
        self.setLEDMode(LimelightLightMode.kOff)

    def limelightOn(self):
        self.setLEDMode(LimelightLightMode.kOn)


    def execute(self):
        """
        limelight functions to run every frame.
        ostensibly, we won't use this at all
        """
        pass
