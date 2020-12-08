import ctre
from . import MotorBase


class TalonSRX(MotorBase, ctre.WPI_TalonSRX):
    pass
