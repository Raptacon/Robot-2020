import json
import yaml
import os
import logging as log
from chardet import detect
from string import ascii_lowercase
from pathlib import Path
from importlib import import_module
from typing import Optional

class FileHandler:
    """
    Various helper methods for finding and loading files/folders.
    """

    @staticmethod
    def load(name):
        """
        Load a .json or .yml file from a directory.
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
    Class to read a config file and parse its contents into a usable format to generate robot objects from
    factories.

    :param robot: Robot to set dicionary attributes to.

    :param config: If desired, specify a config to use. Default is listed in `setup.json`
    """

    def __init__(self, robot, config: Optional[str] = None):

        setup_data = self.load('setup.json')
        default_config = setup_data['default']
        factory_data = self.load('factories.json')

        if config:
            loadedFile = self.load(config)
        else:
            log.warning("No config requested. Using default config: %s" %(default_config))
            loadedFile = self.load(default_config)

        if len(loadedFile) != 2:
            raise ValueError(
                "Config should only have 2 keys, found %s" % len(loadedFile)
            )

        self.compatibility = loadedFile['compatibility']
        subsystems = loadedFile['subsystems']

        # Loop through subsystems and generate factory objects
        for subsystem_name, subsystem_data in subsystems.items():
            for group_name, group_info in subsystem_data.items():

                factory = getattr(import_module(factory_data[group_name]['file']), factory_data[group_name]['func'])
                items = {key:factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                setattr(robot, groupName_subsystemName, items)
                log.info(
                    f"Creating {len(items)} item(s) for '{group_name}' in subsystem {subsystem_name}"
                )

    @staticmethod
    def findConfig() -> str:
        """
        Sets the config to be used on the robot. To manually set a config, run 'echo <config name> > RobotConfig'
        on the robot. This will create a file called 'RobotConfig' on the robot with the config requested.
        It can then be read and processed appropriately.
        This method returns the name of the config file as a string type.

        :param use_encoding: If set to True, use Unicode encoding to read the 'RobotConfig' file
        (this likely won't need to be changed as it should always be used; should only be necessary if encoding fails).
        """

        home = str(Path.home()) + os.path.sep
        configDir = home + 'RobotConfig'

        try:
            with open(configDir, 'rb') as file:
                raw_data = file.readline().strip()
            log.info("Config found in %s" %(configDir))
        except:
            log.warning("Config file 'RobotConfig' could not be found; unable to load. This may be intentional.")
            configString = None
            return configString

        encoding_type = ((detect(raw_data))['encoding']).lower()
        with open(configDir, 'r', encoding = encoding_type) as file:
            configString = file.readline().strip()
        log.info("Using config '%s'" %(configString))

        return configString
