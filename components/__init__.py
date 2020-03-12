
class Dummy:
    def execute(self):
        pass

def dummyFunc(self):
    pass

from networktables import NetworkTables
smartDashboard = NetworkTables.getTable('SmartDashboard')
smartDashboard.putNumber("ballCount", 0)