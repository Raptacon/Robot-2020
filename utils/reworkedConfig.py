# Universal utilities
import logging as log

# Utilities for config files
import os
from pathlib import Path
from chardet import detect
from importlib import import_module
from utils.filehandler import FileHandler

# Utilities for creating/updating controllers
from time import sleep
from wpilib import XboxController
from threading import Thread
from networktables import NetworkTables

# Utilities for creating components
import components
from typing import get_type_hints
from inspect import ismodule, isclass


CONTROLLER_UPDATE_DELAY = 0.020


class _Controller:
    """
    Create a new controller. This class automatically starts a new thread to
    update the controller that is being created.
    """

    def __init__(self, controller: XboxController):

        self.controller = controller

        # Instantiate values to prevent crash in `setup` methods
        self.leftY = 0
        self.leftX = 0
        self.rightY = 0
        self.rightX = 0
        self.leftTrigger = 0
        self.rightTrigger = 0

        def update():
            """
            Update controller values.
            """

            while True:
                sleep(CONTROLLER_UPDATE_DELAY)
                self.leftY = self.controller.getRawAxis(XboxController.Axis.kLeftY)
                self.rightY = self.controller.getRawAxis(XboxController.Axis.kRightY)
                self.leftX = self.controller.getRawAxis(XboxController.Axis.kLeftX)
                self.rightX = self.controller.getRawAxis(XboxController.Axis.kRightX)
                self.rightTrigger = self.controller.getRawAxis(XboxController.Axis.kRightTrigger)
                self.leftTrigger = self.controller.getRawAxis(XboxController.Axis.kLeftTrigger)
                self.POV = self.controller.getPOV()

        updater = Thread(target=update)
        updater.start()
        log.debug(f"Started thread for controller {self.controller}")


class ConfigurationManager(FileHandler):
    """
    Read a config file and generate robot objects from factories,
    create controllers, and create magic components.
    To manually set a config, run `echo {config name} > RobotConfig`
    on the robot. Default is listed in `setup.json`.

    :param robot: Robot to set dicionary attributes to.
    """

    def __init__(self, robot):

        setup = self.load('setup.json')
        default_config = setup['default']
        controllers = setup['controllers']

        def findConfig():

            configDir = str(Path.home()) + os.path.sep + 'RobotConfig'

            try:
                with open(configDir, 'rb') as rf:
                    raw_data = rf.readline().strip()
                encoding_type = ((detect(raw_data))['encoding']).lower()
                with open(configDir, 'r', encoding=encoding_type) as file:
                    configString = file.readline().strip()
                log.info(f"Config found in {configDir}")
            except FileNotFoundError:
                log.error(f"{configDir} could not be found.")
                configString = default_config
            return configString

        config = findConfig()

        log.info(f"Using config '{config}'")
        loadedConfig = self.load(config)

        subsystems = loadedConfig['subsystems']
        self.compatibility = loadedConfig['compatibility']
        factory_data = self.load('factories.json')

        self.__createFactoryObjects(robot, subsystems, factory_data)
        self.__initializeControllers(robot, controllers)
        self.__createComponents(robot)

    def __createFactoryObjects(self, robot, subsystems, factory_data):
        """
        Creates dictionary attributes to set to a robot.
        These are used for variable injection.
        """

        # Generate objects from factories and set them to `robot`
        log.info(f"Creating {len(subsystems)} subsystem(s)")
        total_items = 0
        for subsystem_name, subsystem_data in subsystems.items():
            for group_name, group_info in subsystem_data.items():
                file = import_module(factory_data[group_name]['file'])
                func = factory_data[group_name]['func']
                factory = getattr(file, func)
                items = {key: factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                setattr(robot, groupName_subsystemName, items)
                log.info(
                    f"Created {len(items)} item(s) into '{groupName_subsystemName}'"
                )
                total_items += len(items)
        log.info(f"Created {total_items} total item(s).")

    def __initializeControllers(self, robot, controller_info):

        controllers = {}
        
        for name, port in controller_info.items():
            controllers[name] = _Controller(XboxController(port))
            log.info(f"Created '{name}' controller for port {port}")

        setattr(robot, 'controllers', controllers)
        log.info("Created controller attribute for robot.")

    def __createComponents(self, robot):
        """
        Loops through annotated components on a robot, creating them
        according to the compatibility in the selected configuration.
        """

        components = get_type_hints(robot).items()
        for component_name, component in components:
            if isclass(component):
                self.__testComponentCompatibility(robot, component_name, component)

    def __testComponentCompatibility(self, robot, component_name, component_type):
        """
        Checks the compatibility of a component.
        """

        if not hasattr(component_type, "compatString"):
            robot.logger.warn(
                f"'{component_name}' has no compatString set. Assuming compatible."
            )
            return

        compCompat = component_type.compatString
        compatibility = [self.compatibility]

        if bool(set(compCompat).intersection(compatibility)) \
           or 'all' in compCompat \
           or 'all' in compatibility:
            return

        robot.logger.warn(f"'{component_name}' is not compatible. Disabling")

        # NOTE: Because of we are overriding the default settings in MagicBot's
        #       variable injection by passing components into this method,
        #       we need to manually inject the variables here.

        # Iterate over variables with type annotations
        for n, inject_type in get_type_hints(component_type).items():

            # If the variable is private ignore it
            if n.startswith("_"):
                continue

            # If the variable has been set, skip it
            if hasattr(component_type, n):
                continue

            # Check for generic types from the typing module
            origin = getattr(inject_type, "__origin__", None)
            if origin is not None:
                inject_type = origin

            # If the type is not actually a type, give a meaningful error
            if not isinstance(inject_type, type) and not ismodule(inject_type):
                raise TypeError(
                    "Component %s has a non-type annotation on %s (%r);"
                    "lone non-injection variable annotations are disallowed,"
                    "did you want to assign a static variable?"
                    % (inject_type, n, inject_type)
                )

            # Create any injectables we need
            if not hasattr(robot, n):
                robot.logger.info(f"Creating variable {n} for robot")
                setattr(robot, n, inject_type())

        # Disable functioning parts of disabled components
        component_type.execute = components.dummyFunc
        component_type.on_enable = components.dummyFunc
        component_type.setup = components.dummyFunc
