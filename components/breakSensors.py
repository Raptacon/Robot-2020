from enum import IntEnum

class SensorKey(IntEnum):
    kLoadingSensor = 0
    kShootingSensor = 4

class State:
    kTripped = False
    kNotTripped = True

class Sensors:

    digitalInput_breaksensors: dict

    def on_enable(self):
        self.SensorArray = []
        for x in range(1, 6):
            self.SensorArray.append(self.digitalInput_breaksensors["sensor" + str(x)])
        self.logger.info("Break sensor component created")

    def loadingSensor(self, state):
        """Gets the loading sensor state and checks if it matches the requested state."""
        if self.SensorArray[SensorKey.kLoadingSensor].get() == state:
            return True
        return False

    def shootingSensor(self, state):
        """Gets the shooting sensor state and checks if it matches the requested state."""
        if self.SensorArray[SensorKey.kShootingSensor].get() == state:
            return True
        return False

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

        return self.ballCount

    def execute(self):
        pass
