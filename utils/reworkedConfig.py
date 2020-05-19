import json
import yaml
import os
import logging as log
from chardet import detect
from pathlib import Path
from importlib import import_module

class FileHandler:
    """
    Various helper methods for finding and loading files/folders.
    """

    @staticmethod
    def load(name):
        """
        Load a .json or .yml file.
        """

        directory = FileHandler.file_directory(name)
        _, file_type = os.path.splitext(name)

        with open(directory) as file:
            if file_type == '.json':
                loadedFile = json.load(file)
            elif file_type == '.yml':
                loadedFile = yaml.load(file, yaml.FullLoader)
            else:
                raise NotImplementedError(f"File type '{file_type}' is unsupported.")

        return loadedFile

    @staticmethod
    def file_directory(name) -> str:
        """
        Attempt to get the directory of a requested file.
        """

        path = os.getcwd()

        for root, _, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

        raise NotADirectoryError(f"File '{name}' doesn't exist in {path}")

    @staticmethod
    def folder_directory(name) -> str:
        """
        Attempt to get the directory of a requested folder.
        """

        path = os.getcwd()

        for root, dirs, _ in os.walk(path):
            if name in dirs:
                return os.path.join(root, name)

        raise NotADirectoryError(f"Folder '{name}' doesn't exist in {path}")

    @staticmethod
    def get_all_files(foldername, extentions = False) -> list:
        """
        Lists the names of all the files living within a folder.
        NOTE this function automatically removes `__init__.py`
        from the list.
        """

        path = FileHandler.folder_directory(foldername)
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        filtered_files = []

        for file in files:
            if file.startswith('_'):
                continue
            if not extentions:
                split_file = file.split('.')
                filtered_files.append(split_file[0])
            else:
                filtered_files.append(file)

        return filtered_files

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
