from enum import IntEnum

class Sensors(IntEnum):
    kLoadingSensor = 0
    kShootingSensor = 4

class State:
    kTripped = False
    kNotTripped = True

class BreakSensors:

    robot = ["doof"]

    sensors_breaksensors: dict

    def on_enable(self):
        self.SensorArray = []
        for x in range(1, 6):
            self.SensorArray.append(self.sensors_breaksensors["sensor" + str(x)])
        self.logger.info("Break sensor component created")

    def get(self, sensor, condition):
        if self.SensorArray[sensor].get() == condition:
            return True

    def execute(self):
        pass
