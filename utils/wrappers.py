import components
import os

class RobotTerminatedError(Exception):
    exit(1)

class getComponents:
    def components(self):
        component_count = len([name for name in os.listdir('.') if os.path.isfile(name)])
        print(component_count)

