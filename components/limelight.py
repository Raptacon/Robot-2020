"""
Manager to more easily read the values 
from the limelight and more easily write 
to for pipeline changes
"""
from networktables import NetworkTables
from enum import Enum

class LimelightCamMode(Enum):
    kDriverMode = 1
    kProcessingMode = 0

class LimelightLightMode(Enum):
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

    def _checkForObject(self):
        assert self.limelightTable.getNumber("tx") == 1, "there is no object in view, cannot get offset" #this is pretty weird for me - just let me know or fix it if it is overkill

    def getXOffset(self):
        """
        gets from the network tables how far off the
        crosshair is from the sensed targed. throws an
        error if there is no target in view
        """
        _checkForObject(self)
        return self.limelightTable.getNumber("tx")

    def getYOffset(self):
        pass

    def getSize(self):
        pass

    def setPipeline(self):
        pass

    def setCameraMode(self, mode: LimelightCamMode):
        pass

    def setLEDMode(self, mode: LimelightLightMode):
        pass

    def execute(self):
        pass
