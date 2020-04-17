import json
import os
from os.path import dirname
import logging as log
from chardet import detect
from string import ascii_lowercase
from pathlib import Path
from . import __all__ as modules

class ConfigMapper:

    def __init__(self, robot, fileName: str, specifiedConfig = None):
        #self.robot = robot
        self.configFileName = fileName
        loadedFile = self.__loadFile(fileName)
        config, configName = self.__getConfig(loadedFile, requestedConfig = specifiedConfig)

        self.configName = configName
        self.configCompat = config['compatibility']

        self.testStuff(config)

    def __loadFile(self, fileName):
        configFile = dirname(__file__) + os.path.sep + '..' + os.path.sep + fileName
        with open(configFile) as file:
            loadedFile = json.load(file)
        return loadedFile

    def __getConfig(self, configFile, requestedConfig = None):
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
            )

        # Return filtered config and name of config
        return config, configName

    def testStuff(self, config):
        for group, data in config.items():
            if isinstance(data, list):
                for dictionary in data:
                    if 'factory' in dictionary:
                        factory = dictionary['factory']
                    if 'subsystem' in dictionary:
                        subsystem_name = dictionary.pop('subsystem')
                        subsystem = dictionary
                        print(f"Group Name: {group}, Subsystem Name: {subsystem_name}, Factory: {factory}, Group: {subsystem}")
                        print('blah', modules)

    def almostThere(self, robot, groupName, subsystemName, group, factory_name):
        pass

    def checkCompatibility(self, compatString):
        """
        Checks compatibility of the component based on the compatString and the compatibility key in the config.
        """

        compatString = [x.lower() for x in compatString]
        root = [self.configCompat] # This is the compatibility of the loaded config
        if "all" in root or "all" in compatString:
            return True
        for string in root:
            if string in compatString:
                return True
        return False

def findConfig(use_encoding = True, strict = False):
    """
    Sets the config to be used one the robot. To manually set a config, run 'echo [config name] > RobotConfig' on the robot.
    This will create a file called 'RobotConfig' on the robot with the config requested.
    It can then be read and processed appropriately.
    This method returns the name of the config as a string type.

    :param use_encoding: If set to True, use Unicode encoding to read the 'RobotConfig' file
    (this likely wont need to be changed as it should always be used; should only be necessary if encoding fails).

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
            raise FileNotFoundError("No 'RobotConfig' file found, unable to read contents. Aborting.")

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
        log.warning("Config requested '%s' had uppercase characters, which have been lowered." %(configString))
        configString = configString.lower()

    return configString

if __name__ == '__main__':
    configMapper = ConfigMapper(None, 'robot.json')
