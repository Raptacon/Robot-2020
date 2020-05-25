import os
import logging as log
from pathlib import Path
from chardet import detect
from importlib import import_module
from utils.filehandler import FileHandler

# Utilities for creating components
import components
from typing import get_type_hints
from inspect import ismodule, isclass


class ConfigurationManager(FileHandler):
    """
    Read a config file and generate robot objects from factories.
    To manually set a config, run `echo {config name} > RobotConfig`
    on the robot. Default is listed in `setup.json`.

    :param robot: Robot to set dicionary attributes to.
    """

    def __init__(self, robot):

        def findConfig():

            default_config = (self.load('setup.json'))['default']
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

        self.compatibility = loadedConfig['compatibility']

        # Generate objects from factories and set them to `robot`
        subsystems = loadedConfig['subsystems']
        factory_data = self.load('factories.json')
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

        self.__createComponents(robot)

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
