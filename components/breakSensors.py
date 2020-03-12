from enum import IntEnum
from . import smartDashboard

class Index(IntEnum):
    kLoadingSensor = 0
    kSecondBottom = 1
    kMiddle = 2
    kSecondTop = 3
    kShootingSensor = 4

class State:
    kTripped = False
    kNotTripped = True

class Sensors:

    digitalInput_breaksensors: dict

    def on_enable(self):
        smartDashboard.putNumber("ballCount", 0)
        self.SensorArray = []
        for x in range(1, 6):
            self.SensorArray.append(self.digitalInput_breaksensors["sensor" + str(x)])
        self.logger.info("Break sensor component created")

    def getSensor(self, index, state):
        """
        Returns if the state of a sensor at index matches the parameter state
        """
        if self.SensorArray[index].get() == state:
            return True
        return False

    def calcBallCount(self):
        """
        Counts the number of sensors broken and returns that number
        """
        self.ballCount = 0
        for sensor in self.SensorArray:
            if sensor.get() == State.kTripped:
                self.ballCount += 1

        smartDashboard.putNumber("ballCount", self.ballCount)
        return self.ballCount

    def execute(self):
        pass
