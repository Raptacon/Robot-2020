import os
import logging as log
from chardet import detect
from pathlib import Path
from importlib import import_module
from utils.filehandler import FileHandler

class ConfigurationManager(FileHandler):
    """
    Read a config file and generate robot objects from factories.
    To manually set a config, run `echo <config name> > RobotConfig` on the robot.
    Default is listed in `setup.json`.

    :param robot: Robot to set dicionary attributes to.
    """

    def __init__(self, robot):

        default_config = (self.load('setup.json'))['default']

        def findConfig():

            configDir = str(Path.home()) + os.path.sep + 'RobotConfig'

            try:
                with open(configDir, 'rb') as file:
                    raw_data = file.readline().strip()
                log.info(f"Config found in {configDir}")
                encoding_type = ((detect(raw_data))['encoding']).lower()
                with open(configDir, 'r', encoding = encoding_type) as file:
                    configString = file.readline().strip()
            except FileNotFoundError:
                log.error(f"{configDir} could not be found.")
                configString = default_config
            finally:
                return configString

        config = findConfig()

        log.info(f"Using config '{config}'")
        loadedConfig = self.load(config)

        self.compatibility = loadedConfig['compatibility']
        subsystems = loadedConfig['subsystems']
        factory_data = self.load('factories.json')

        log.info(f"Creating {len(subsystems)} subsystems")

        # Generate robot objects from factories
        for subsystem_name, subsystem_data in subsystems.items():
            for group_name, group_info in subsystem_data.items():
                factory = getattr(import_module(factory_data[group_name]['file']), factory_data[group_name]['func'])
                items = {key:factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                setattr(robot, groupName_subsystemName, items)
                log.info(f"Created {len(items)} item(s) into '{groupName_subsystemName}'")
