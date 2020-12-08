import wpilib
import ctre
import rev
import navx

from abc import ABC, abstractmethod


_MOTORS = {}


def create_motor(desc):

    typ = desc["type"]
    motor_cls = _MOTORS.get(typ, None)
    if motor_cls is None:
        raise AttributeError(
            f"could not find motor object for {typ!r}"
        )
    motor = motor_cls(desc)

    if "pid" in desc:
        motor.setup_PID(desc["pid"])
    if "currentLimits" in desc:
        motor.set_currentlimits(desc["currentLimits"])

    return motor


class _MotorBase(ABC):
    
    def __init_subclass__(cls):
        typ = getattr(cls, "__type__", None)
        if typ is None:
            raise AttributeError(
                f"could not find motor type for {cls!r}"
            )
        _MOTORS.update({typ: cls})

    @abstractmethod
    def setup_PID(self):
        pass

    @abstractmethod
    def set_currentlimits(self):
        pass

    @abstractmethod
    def set(self):
        pass


class TalonSRX(_MotorBase):

    __type__ = "CANTalonSRX"

    def __init__(self, desc):
        pass

    def setup_PID(self, pid_desc):
        pass

    def set_currentlimits(self, cl_desc):
        pass

    def set(self, speed):
        pass


class TalonFX(_MotorBase):

    __type__ = "CANTalonFX"

    def __init__(self, desc):
        pass

    def setup_PID(self, pid_desc):
        pass

    def set_currentlimits(self, cl_desc):
        pass

    def set(self, speed):
        pass


class SparkMax(_MotorBase):

    __type__ = "CANSparkMax"

    def __init__(self, desc):
        pass

    def setup_PID(self, pid_desc):
        pass

    def set_currentlimits(self, cl_desc):
        pass

    def set(self, speed):
        pass
