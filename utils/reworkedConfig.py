import json
import os
import inspect
import logging as log
from chardet import detect
from string import ascii_lowercase
from pathlib import Path
from importlib import import_module
from typing import Optional

if __name__ != '__main__':
    from factories import factory_modules
    import factories
    # NOTE This is only for flake8
    factories.dummy()
else:
    factory_modules = None

class FileHandler:
    """
    Various helper methods for finding and loading files.
    """

    @staticmethod
    def load(directory):
        with open(directory) as file:
            loadedFile = json.load(file)
        return loadedFile

    @staticmethod
    def directory(name):
        """
        Attempt to get the directory of a requested file.
        """

        path = os.getcwd()

        for root, dirs, files in os.walk(path):
            del dirs
            if name in files:
                return os.path.join(root, name)

class ConfigurationManager(FileHandler):
    """
    Class to read a config file and parse its contents into a usable format to generate robot objects from
    factories.

    :param config: If desired, specify a config to use. Default is listed in setup.json
    """

    def __init__(self, config: Optional[str] = None):

        #
        # NOTE: Many instance variables declared here aren't used elsewhere within the class,
        #       rather they are used for validating a config in the `if __name__ == '__main__'`
        #       portion of this file.
        #

        setup_data = self.load(self.directory('setup.json'))
        default_config, requirements, factory_data = self.__getSetupInfo(setup_data)

        try:
            _dir = self.directory(config)
            self.configName = config
        except FileNotFoundError:
            log.warning("No config requested. Using default config: %s" %(default_config))
            _dir = self.directory(default_config)
            self.configName = default_config

        loadedFile = self.load(_dir)

        if __name__ != '__main__':
            self.robot = inspect.stack()[1][0].f_locals["self"]

        self.configCompat, self.subsystems = self.__getConfigInfo(loadedFile, requirements)

        # Loop through subsystems and pass data into function that generates objects from factories
        for subsystem_name, subsystem_data in self.subsystems.items():
            self.__generateFactoryObjects(factory_data, subsystem_name, subsystem_data)

    def __getSetupInfo(self, file):

        default = file['default']
        requirements = file['requirements']
        factory_data = file['factories']

        return default, requirements, factory_data

    def __getConfigInfo(self, file, requirements):
        """
        Takes data from a config file and extracts all the keys.
        """

        attributes = []
        for attr in file:
            attributes.append(attr)
        for requirement in requirements:
            if requirement not in attributes:
                raise AttributeError(
                    f"Required attribute '{requirement}' missing in '{self.configName}'"
                )

        configCompat = file['compatibility']
        subsystems = file['subsystems']

        return configCompat, subsystems

    def __generateFactoryObjects(self, factory_data, subsystem_name, subsystem_data):
        """
        Generates objects from factories based on information from a config. It then sets dictionary
        attributes to a specifed robot to be used for variable injection.
        """

        factory = None

        if factory_modules is None:
            return

        for group_name, group_info in subsystem_data.items():
            if group_name in factory_data:
                factory_name = factory_data[group_name]
                for file in factory_modules:
                    factory_module = 'factories.' + file
                    factory_file = import_module(factory_module)
                    if hasattr(factory_file, factory_name):
                        factory = eval(factory_module + '.' + factory_name)
                if factory is None:
                    raise AttributeError(f"Factory '{factory_name}' doesn't exist in the 'factories' directory.")
            else:
                raise AttributeError(f"Group '{group_name}' has no associated factory.")

            containerName = group_name[0].upper() + group_name[1:]

            if not hasattr(self.robot, containerName):
                setattr(self.robot, containerName, {})

            container = getattr(self.robot, containerName)

            items = {key:factory(descp) for key, descp in group_info.items()}
            created_count = len(items)
            groupName_subsystemName = '_'.join([group_name, subsystem_name])
            container[subsystem_name] = items
            setattr(self.robot, groupName_subsystemName, container[subsystem_name])
            log.info(
                f"Creating {created_count} item(s) for '{group_name}' in subsystem {subsystem_name}"
            )

    def checkCompatibility(self, compatString) -> bool:
        """
        Checks compatibility of the component based on the compatString and the compatibility key in the config.
        """

        compatString = [x.lower() for x in compatString]
        compatString = ''.join(compatString) # FIXME

        root = [self.configCompat] # This is the compatibility of the loaded config
        if "all" in root or "all" in compatString:
            return True
        for string in root:
            if string in compatString:
                return True
        return False

def findConfig(use_encoding = True) -> str:
    """
    Sets the config to be used on the robot. To manually set a config, run 'echo <config name> > RobotConfig' on the robot.
    This will create a file called 'RobotConfig' on the robot with the config requested.
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

    if use_encoding:
        encoding_type = ((detect(raw_data))['encoding']).lower()
        with open(configDir, 'r', encoding = encoding_type) as file:
            configString = file.readline().strip()
        log.info("Using config '%s'" %(configString))
    else:
        valid_chars = []
        alphabet = list(ascii_lowercase)
        alphabet.append('.') # Necessary to specify '.json' file extention
        with open(configDir) as file:
            raw_string = file.readline().strip()
            for char in raw_string:
                if char.isupper():
                    char = char.lower()
                if char in alphabet:
                    valid_chars.append(char)
        configString = ''.join(valid_chars)

    if not configString:
        log.error("Config requested in unreadable, likely due to the file being empty; unable to load.")
        configString = None

    return configString

if __name__ == '__main__':

    mapper = ConfigurationManager(findConfig())

    configCompat = mapper.configCompat
    configName = mapper.configName

    print('')
    print("Config Name:", configName, '\n')

    for subsystem_name, subsystem_data in mapper.subsystems.items():
        print("Subsystem:", subsystem_name)
        for group_name, group_data in subsystem_data.items():
            print("Group: %s: %s" %(group_name, group_data))
        print('')

    dummyConfigString = 'doof'
    isCompatible = mapper.checkCompatibility(dummyConfigString)
    print(f"Is '{dummyConfigString}' compatible with '{configCompat}'? {isCompatible}")
