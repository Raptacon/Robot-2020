import json
import logging as log
from os.path import dirname
import os
from pathlib import Path
from chardet import detect
from string import ascii_lowercase

class ConfigMapper:
    """
    Class to accept a .json config file and 'config' argument.
    This parses the information in the file into a python dictionary.

    :param fileName: Name of the file to be loaded. NOTE this file must be in the root directory.

    :param config: Name of the config to look for and load.
    """

    #log.basicConfig(level=log.INFO)

    def __init__(self, fileName: str, config = None):
        self.configFileName = fileName
        loadedFile = self.__loadFile(fileName)
        config, configName = self.__getConfig(loadedFile, requestedConfig = config)
        self.currentConfig = configName # NOTE: This is used only for testing
        self.configCompat = config['compatibility']
        self.extractedSubsystems = {}
        self.subsystems = self.__extractSubsystems(config)

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

        # Search for any subconfigs, then load and add to config
        if 'subconfigs' in config:
            subconfigs = config['subconfigs']
            for subconfig in subconfigs:
                config[subconfig] = configFile[subconfig]

        # Add 'compatibility' key to config
        config['compatibility'] = configFile[configName]['compatibility']

        # Return filtered config and name of config
        return config, configName

    def __extractSubsystems(self, fileInfo):
        """
        Finds all the subsystems in the config, extracts them, and places them in a new dictionary.
        """

        for key, data in fileInfo.items():
            if 'subsystem' in data and isinstance(data, dict):
                subsystemName = data['subsystem']
                subsystem = fileInfo[key]
                self.extractedSubsystems[subsystemName] = subsystem

        return self.extractedSubsystems

    def __getSubsystemDicts(self, subsystem, groupName):
        """
        Internally processes a subsystem, returning a dict of specific information.
        A 'groupName' is required to determine what factory to use. This is the name used in the config file under 'groups'.
        This information is typically used in the factories.
        """

        updatedSubsystem = {}

        # Loops through subsystem dict and finds nested dicts. When it finds one, dig deeper by running process again
        # This specifically assures that it wont look deeper if it encounters 'groups' key
        for key in subsystem:
            if isinstance(subsystem[key], dict) and 'groups' not in subsystem:
                updatedValues = self.__getSubsystemDicts(subsystem[key], groupName)
                updatedSubsystem.update(updatedValues)

            # After searching, update new dict with values/dicts beyond 'groups' key based on a groupName
            if 'groups' in subsystem[key]:
                if groupName in subsystem[key]["groups"]:
                    updatedSubsystem.update(subsystem[key])

            # Remove 'groups' key from new dict
            if 'groups' in updatedSubsystem:
                updatedSubsystem.pop('groups')

        return updatedSubsystem

    def getSubsystem(self, subsystem):
        """
        Returns the complete config for a specified subsystem. If none is found, return 'None'.
        """

        if subsystem in self.subsystems:
            return self.subsystems[subsystem]
        raise AttributeError("Subsystem '%s' not found, unable to retrieve." %(subsystem))

    def getSubsystems(self):
        """
        Returns a list of the subsystem names.
        """

        subsystems = list(self.subsystems.keys())
        return subsystems

    def getGroupDict(self, subsystem, groupName):
        """
        Retrieves important values from a specified subsystem and returns them as a dictionary.
        """

        rawSubsystem = self.getSubsystem(subsystem)
        subsystemDict = self.__getSubsystemDicts(rawSubsystem, groupName)
        return subsystemDict

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
    """
    Standard testing for elements of the config. To run this, simply run the python file by itself.
    """

    config = findConfig()

    mapper = ConfigMapper('robot.json', config = config)

    print("Config to be used:", mapper.currentConfig)

    subsystemList = mapper.getSubsystems()
    print("Subsystem list:", subsystemList, '\n')

    # NOTE that these are the group names as of the time of this writing. They may change in the future.
    groupNames = ['motors', 'gyros', 'digitalInput', 'compressors', 'solenoids']
    print("groupNames:", groupNames, '\n')

    for subsystem in subsystemList:
        subsys = mapper.getSubsystem(subsystem)
        print("Subsystem %s: %s \n" %(subsystem, subsys))
        for groupName in groupNames:
            groupDicts = mapper.getGroupDict(subsystem, groupName)
            if not len(groupDicts) == 0:
                print("Group dicts %s: %s \n \n" %(subsystem, groupDicts))

    exampleCompatString = ['doof']
    isCompatible = mapper.checkCompatibility(exampleCompatString)
    print("Is %s compatible with '%s'? %s" %(exampleCompatString, mapper.currentConfig, isCompatible))
