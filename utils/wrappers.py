from . import __all__
from utils.componentUtils import testComponentCompatibility

class RobotTerminatedError(Exception):
    exit(1)

def createComponents(robot):
    for module in __all__:
        component = module[0].upper() + module[1:]
        testComponentCompatibility(robot, component)
