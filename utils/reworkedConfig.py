import json
import os
import logging as log
from os.path import dirname
from chardet import detect
from string import ascii_lowercase
from pathlib import Path
from importlib import import_module

try:
    from factories import factory_modules
    import factories
except ImportError:
    if __name__ != '__main__':
        raise
    else:
        factory_modules = None

if __name__ != '__main__':
    # NOTE This is only for flake8
    factories.dummy()

class ConfigMapper:
    """
    Class to accept a config file, config to use, and robot to map config to. This class is designed exclusively
    for ONE .json config file.

    :param robot: Robot to set dictionary attributes to.

    :param filename: Config file to load.

    :param specifiedConfig: If desired, specify a config to use. Default is 'doof'.
    """

    def __init__(
        self,
        robot,
        fileName: str,
        config = None,
        ):

        self.robot = robot
        self.configFileName = fileName
        loadedFile = self.__loadFile(fileName)

        (
            factory_data,
            self.configName, # Used for testing
            self.configCompat, # Used for testing
            self.subsystems
        ) = self.__getConfigInfo(loadedFile, requestedConfig = config)

        # Loop through subsystems and pass data into function that generates objects from factories
        for subsystem_name, subsystem_data in self.subsystems.items():
            self.__generateFactoryObjects(factory_data, subsystem_name, subsystem_data)

    def __loadFile(self, fileName):
        configFile = dirname(__file__) + os.path.sep + '..' + os.path.sep + fileName
        with open(configFile) as file:
            loadedFile = json.load(file)
        return loadedFile

    def __getConfigInfo(self, configFile, requestedConfig = None):
        """
        Method takes a file name as the config file and finds a requested config for the robot, changing it appropriatly.
        If no config is requested, use the default config listed in the file.
        """

        config = {}
        defaultConfig = configFile['default']
        robotConfigs = []

        # Create a list of all robot configs (excluding subconfigs)
        # NOTE: For a config to be defined as a robot config, a 'compatibility' key must be declared
        for key in configFile:
            if 'compatibility' in configFile[key]:
                robotConfigs.append(key)

        # If no requested config, use default
        if requestedConfig == None:
            log.warning("No config requested. Using default: %s" %(defaultConfig))
            config.update(configFile[defaultConfig])
            configName = defaultConfig

        # Find requested config in list of config names, then use
        elif requestedConfig in robotConfigs:
            log.info("Requsted config '%s' found in %s. Loading..." %(requestedConfig, self.configFileName))
            config.update(configFile[requestedConfig])
            configName = requestedConfig

        # If requested config isn't found, raise error and exit
        else:
            raise AttributeError(
                """
                Requested config '%s' could not be found. Current configs: %s.
                Is there a 'compatibility' key in '%s'?
                """ %(requestedConfig, robotConfigs, requestedConfig)
            ) # TODO: Add 'strict' option to choose not to raise error if config is not found, rather use default

        # Get factory information
        factory_data = configFile['factories']

        # Get config compatibility
        configCompat = config['compatibility']

        # Get subsystems
        subsystems = config['subsystems']

        # Return specific config info
        return factory_data, configName, configCompat, subsystems

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
            else:
                raise AttributeError(f"Group '{group_name}' has no associated factory.")

            containerName = group_name[0].upper() + group_name[1:]

            if not hasattr(self.robot, containerName):
                setattr(self.robot, containerName, {})

            container = getattr(self.robot, containerName)

            if factory is not None:
                items = {key:factory(descp) for key, descp in group_info.items()}
                groupName_subsystemName = '_'.join([group_name, subsystem_name])
                container[subsystem_name] = items
                setattr(self.robot, groupName_subsystemName, container[subsystem_name])
            else:
                raise AttributeError(f"Factory '{factory_name}' doesn't exist in the 'factories' directory.")

    def checkCompatibility(self, compatString) -> bool:
        """
        Checks compatibility of the component based on the compatString and the compatibility key in the config.
        """

        compatString = [x.lower() for x in compatString]
        compatString = ''.join(compatString)

        root = [self.configCompat] # This is the compatibility of the loaded config
        if "all" in root or "all" in compatString:
            return True
        for string in root:
            if string in compatString:
                return True
        return False

def findConfig(use_encoding = True, strict = False) -> str:
    """
    Sets the config to be used on the robot. To manually set a config, run 'echo <config name> > RobotConfig' on the robot.
    This will create a file called 'RobotConfig' on the robot with the config requested.
    It can then be read and processed appropriately.
    This method returns the name of the config as a string type.

    :param use_encoding: If set to True, use Unicode encoding to read the 'RobotConfig' file
    (this likely won't need to be changed as it should always be used; should only be necessary if encoding fails).

    :param strict: If set to True, will raise an error and exit anytime the contents of the file aren't able to be processed
    (as opposed to returning the default value None). This includes requiring a config file to be present.
    """

    home = str(Path.home()) + os.path.sep
    configDir = home + 'RobotConfig'

    try:
        with open(configDir, 'rb') as file:
            raw_data = file.readline().strip()
        log.info("Config found in %s" %(configDir))
    except:
        if not strict:
            log.warning("Config file 'RobotConfig' could not be found; unable to load. This may be intentional.")
            configString = None
            return configString
        else:
            raise FileNotFoundError(
                "No 'RobotConfig' file found in %s, unable to read contents. Aborting." %(home)
            )

    if use_encoding:
        encoding_type = ((detect(raw_data))['encoding']).lower()
        with open(configDir, 'r', encoding = encoding_type) as file:
            configString = file.readline().strip()
    else:
        valid_chars = []
        alphabet = list(ascii_lowercase)
        with open(configDir) as file:
            raw_string = file.readline().strip()
            for char in raw_string:
                if char.isupper():
                    char = char.lower()
                if char in alphabet:
                    valid_chars.append(char)
        configString = ''.join(valid_chars)

    if not configString:
        if not strict:
            log.error("Config requested in unreadable, likely due to the file being empty; unable to load.")
            configString = None
        else:
            raise SyntaxError(
                "Config requested in unreadable, likely due to the file being empty; unable to load. Aborting."
            )

    if not all(char.isalpha() for char in configString):
        invalid_chars = [char for char in configString if not char.isalpha()]
        raise SyntaxError(
            "Config '%s' has special character(s) %s which are disallowed." %(configString, invalid_chars)
        )

    if any(char.isupper() for char in configString):
        log.warning("Config requested '%s' has uppercase characters, which have been lowered." %(configString))
        configString = configString.lower()

    return configString

if __name__ == '__main__':

    mapper = ConfigMapper(None, 'robot.json', config = findConfig())

    configFileName = mapper.configFileName
    configCompat = mapper.configCompat
    configName = mapper.configName

    print('')
    print("Config File:", configFileName)
    print("Config Name:", configName, '\n')

    for subsystem_name, subsystem_data in mapper.subsystems.items():
        print("Subsystem:", subsystem_name)
        for group_name, group_data in subsystem_data.items():
            print("Group: %s: %s" %(group_name, group_data))
        print('')

    dummyConfigString = 'doof'
    isCompatible = mapper.checkCompatibility(dummyConfigString)
    print(f"Is '{dummyConfigString}' compatible with '{configCompat}'? {isCompatible}")
