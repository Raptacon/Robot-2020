from abc import ABC, abstractmethod


class MotorBase(ABC):

    def __init_subclass__(cls):
        bases = cls.__bases__
        if len(bases) < 2:
            raise AttributeError(
                 "motor objects inheriting from MotorBase "
                 "must also inherit from a base motor class "
                f"(raised with {cls!r}, bases: {bases})"
            )

    @abstractmethod
    def setup_PID(self):
        pass

    @abstractmethod
    def set_currentlimits(self):
        pass

    @abstractmethod
    def set(self):
        pass
