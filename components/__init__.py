
class Dummy:
    def execute(self):
        pass

def dummyFunc(self):
    pass

from networktables import NetworkTables
NetworkTables.initialize(server='roborio-3200-frc.local')
smartDashboard = NetworkTables.getTable('SmartDashboard')