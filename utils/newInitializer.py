# Utilities for loading/using robot configs
import os
from pathlib import Path
from chardet import detect
from importlib import import_module
from utils.filehandler import FileHandler

# Utilities for creating/updating controllers
from time import sleep
from wpilib import XboxController
from threading import Thread


CONTROLLER_UPDATE_DELAY = 0.020


class InitializeRobot(FileHandler):
    """
    Read a config file and generate robot objects from factories,
    create controllers, and create magic components.
    To manually set a config, run `echo {config name} > RobotConfig`
    on the robot. Default is listed in `setup.json`.

    :param robot: Robot to set dicionary attributes to.
    """

    def __init__(self, robot, config_file=None):

        try:
            config_data = self.load(config_file)
        except:
            raise TypeError(f"Must specify a config file for {robot.__name__}.")

        self.compatibility = config_data['compatibility']
        controllers = config_data['controllers']
        subsystems = config_data['subsystems']
        factory_data = self.load('factories.json')

        self.__createFactoryObjects(robot, subsystems, factory_data)
        self.__initializeControllers(robot, controllers)

    def __createFactoryObjects(self, robot, subsystems, factory_data):
        """
        Creates dictionary attributes to set to a robot.
        These are used for variable injection.
        """

        # Generate objects from factories and set them to `robot`
        robot.logger.info(f"Creating {len(subsystems)} subsystem(s)")
        total_items = 0
        for subsystem_name, subsystem_data in subsystems.items():
            for group_name, group_info in subsystem_data.items():
                file = import_module(factory_data[group_name]['file'])
                func = factory_data[group_name]['func']
                factory = getattr(file, func)
                items = {key: factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                setattr(robot, groupName_subsystemName, items)
                robot.logger.info(
                    f"Created {len(items)} item(s) into '{groupName_subsystemName}'"
                )
                total_items += len(items)
        robot.logger.info(f"Created {total_items} total item(s).")

    def __initializeControllers(self, robot, controller_info):
        """
        Creates controller attributes to set to a robot.
        """

        controllers = {}

        class _Controller:
            """
            Create a new controller. This class automatically starts a new
            thread to update the controller that is being created.
            """

            def __init__(self, controller: XboxController):

                self.controller = controller

                def update():
                    """
                    Update controller values.
                    """

                    while True:
                        sleep(CONTROLLER_UPDATE_DELAY)
                        self.leftY = self.controller.getRawAxis(
                            XboxController.Axis.kLeftY)
                        self.leftX = self.controller.getRawAxis(
                            XboxController.Axis.kLeftX)
                        self.rightY = self.controller.getRawAxis(
                            XboxController.Axis.kRightY)
                        self.rightX = self.controller.getRawAxis(
                            XboxController.Axis.kRightX)
                        self.leftTrigger = self.controller.getRawAxis(
                            XboxController.Axis.kLeftTrigger)
                        self.rightTrigger = self.controller.getRawAxis(
                            XboxController.Axis.kRightTrigger)
                        self.pov = self.controller.getPOV()

                updater = Thread(target=update)
                updater.start()
                robot.logger.debug(f"Started thread for controller {self.controller}")

        for name, port in controller_info.items():
            controllers[name] = _Controller(XboxController(port))
            robot.logger.info(f"Created '{name}' controller for port {port}")

        setattr(robot, 'controllers', controllers)
        robot.logger.info("Created controller attribute for robot.")
