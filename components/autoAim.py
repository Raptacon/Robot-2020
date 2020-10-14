from networktables import NetworkTables as nt

class AutoAim:

    table = nt.getTable("limelight")
    tx = table.getNumber('tx', None)

    def aimAndShoot(self):
        pass

