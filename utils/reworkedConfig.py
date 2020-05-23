import os
import logging as log
from pathlib import Path
from chardet import detect
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

        # Generate objects from factories
        subsystems = loadedConfig['subsystems']
        factory_data = self.load('factories.json')
        log.info(f"Creating {len(subsystems)} subsystem(s)")
        for subsystem_name, subsystem_data in subsystems.items():
            for group_name, group_info in subsystem_data.items():
                _file = import_module(factory_data[group_name]['file'])
                _func = factory_data[group_name]['func']
                factory = getattr(_file, _func)
                items = {key:factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                setattr(robot, groupName_subsystemName, items)
                log.info(f"Created {len(items)} item(s) into '{groupName_subsystemName}'")
