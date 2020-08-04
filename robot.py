# # Module imports:
# from wpilib import XboxController, run
# from magicbot import MagicRobot

# # Component imports:
# from components.driveTrain import DriveTrain
# from components.pneumatics import Pneumatics
# from components.buttonManager import ButtonManager, ButtonEvent
# from components.breakSensors import Sensors
# from components.winch import Winch
# from components.shooterMotors import ShooterMotorCreation
# from components.shooterLogic import ShooterLogic
# from components.loaderLogic import LoaderLogic
# from components.elevator import Elevator
# from components.scorpionLoader import ScorpionLoader
# from components.feederMap import FeederMap

# # Other imports:
# from utils.robotInitializer import InitializeRobot

# class MyRobot(MagicRobot):
#     """
#     Base robot class of Magic Bot Type
#     """
#     shooter: ShooterLogic
#     loader: LoaderLogic
#     feeder: FeederMap
#     sensors: Sensors
#     shooterMotors: ShooterMotorCreation
#     driveTrain: DriveTrain
#     winch: Winch
#     buttonManager: ButtonManager
#     pneumatics: Pneumatics
#     elevator: Elevator
#     scorpionLoader: ScorpionLoader

#     controllers: dict

#     def createObjects(self):
#         """
#         Robot-wide initialization code should go here. Replaces robotInit
#         """

#         self.initializer = InitializeRobot(self)

#     def autonomousInit(self):
#         """Run when autonomous is enabled."""
#         self.shooter.autonomousEnabled()
#         self.loader.stopLoading()

#     def teleopInit(self):

#         # Controller definitions
#         mech = self.controllers['mech'].controller
#         drive = self.controllers['drive'].controller

#         # Other definitions
#         compatibility = self.initializer.compatibility
#         Button = XboxController.Button
#         event = self.buttonManager.registerButtonEvent

#         # Register button events for doof
#         if compatibility == 'doof':
#             event(mech, Button.kX, ButtonEvent.kOnPress, self.pneumatics.toggleLoader)
#             event(mech, Button.kY, ButtonEvent.kOnPress, self.loader.setAutoLoading)
#             event(mech, Button.kB, ButtonEvent.kOnPress, self.loader.setManualLoading)
#             event(mech, Button.kA, ButtonEvent.kOnPress, self.shooter.shootBalls)
#             event(mech, Button.kA, ButtonEvent.kOnPress, self.loader.stopLoading)
#             event(mech, Button.kA, ButtonEvent.kOnRelease, self.shooter.doneShooting)
#             event(mech, Button.kA, ButtonEvent.kOnRelease, self.loader.determineNextAction)
#             event(mech, Button.kBumperRight, ButtonEvent.kOnPress, self.elevator.setRaise)
#             event(mech, Button.kBumperRight, ButtonEvent.kOnRelease, self.elevator.stop)
#             event(mech, Button.kBumperLeft, ButtonEvent.kOnPress, self.elevator.setLower)
#             event(mech, Button.kBumperLeft, ButtonEvent.kOnRelease, self.elevator.stop)
#             event(drive, Button.kBumperLeft, ButtonEvent.kOnPress, self.driveTrain.enableCreeperMode)
#             event(drive, Button.kBumperLeft, ButtonEvent.kOnRelease, self.driveTrain.disableCreeperMode)

#         # Register button events for scorpion
#         elif compatibility == 'scorpion':
#             self.logger.warning("Robot 'scorpion' has no button events.")

#         # Register button events for minibot
#         elif compatibility == 'minibot':
#             self.logger.warning("Robot 'minibot' has no button events.")

#         else:
#             self.logger.error(
#                 f"Robot '{compatibility}' is not a recognized"
#                 "robot for button events."
#             )

#         self.shooter.autonomousDisabled()

#     def teleopPeriodic(self):
#         """
#         Must include. Called running teleop.
#         """
#         pass

from sys import argv
from os import system
from utils.filehandler import FileHandler
from pathlib import Path
from chardet import detect
import os
import wpilib

from magicbot import MagicRobot
import magicbot.magicrobot as mb
from importlib import import_module
from inspect import isclass, getmembers
from robotpy_ext.autonomous import AutonomousModeSelector

from networktables import NetworkTables
from robotpy_ext.misc.simple_watchdog import SimpleWatchdog


# log = logger.getLogger()
# log.setLevel(logger.INFO)

# NOTE: Print statements should be avoided in general, but
#       logging is tricky with the robots.

def findConfig():

    default_config = 'doof'

    config_dir = str(Path.home()) + os.path.sep + 'RobotConfig'

    try:
        with open(config_dir, 'rb') as rf:
            raw_data = rf.readline().strip()
        encoding_type = ((detect(raw_data))['encoding']).lower()
        with open(config_dir, 'r', encoding=encoding_type) as file:
            configString = file.readline().strip()
        print(f"Config found in {config_dir}")
    except FileNotFoundError:
        print(f"{config_dir} could not be found.")
        configString = default_config
    return configString


if __name__ == '__main__':

    config = findConfig()
    print(f"Using config {config}")
    robot_file = FileHandler.file_directory(
                    config if '.py' in config else (config + '.py')
                )
    
    argv.remove('robot.py')
    command = 'py ' + robot_file + ' ' + ' '.join(argv)
    system(command)


