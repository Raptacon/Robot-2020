import ctre
from . import MotorBase


class TalonFX(MotorBase, ctre.WPI_TalonFX):
    pass
