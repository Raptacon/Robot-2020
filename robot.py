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
from os import system as cmd
from utils.filehandler import FileHandler


if __name__ == '__main__':
    robot_file = FileHandler.file_directory('doof.py')
    cmd('py ' + robot_file + ' ' + argv[1])

