import yaml
import logging as log
from pprint import pprint
import os
from pathlib import Path

class IncorrectFileTypeError(Exception):
    """
    Thrown when the key 'file' in the config file is not 'yaml'.
    """
    pass

class NoCompatibilityError(Exception):
    """
    Thrown when the config file has no 'compatibility' key.
    """
    pass

class ConfigMapper:
    """
    Class used to handle most config/file related activites.
    """
    # NOTE: All methods starting with '__' are PRIVATE, meaning they aren't used outside of this file.
    def __init__(self, fileName, configDir):
        self.configDir = configDir
        loadedFile = self.__loadFile(fileName)
        self.extractedSubsystems = {}
        self.subsystems = self.__extractSubsystems(loadedFile)
        try:
            self.configCompat = loadedFile['compatibility']
        except NoCompatibilityError:
            log.error("No compatibility key found in config file. Unable to bind correct components.")

    def __loadFile(self, fileName):
        """
        Loads a yaml file and returns the contents as a dictionary.
        """
        with open(self.configDir + os.path.sep + fileName) as file:
            loadedFile = yaml.load(file, yaml.FullLoader)
            return loadedFile

    def __extractSubsystems(self, fileInfo):
        """
        Finds all the subsystems in a config file and returns their names as dictionaries.
        If a file must be loaded, it's loaded and the subsystems are read/created.
        """
        for key, data in fileInfo.items():
            if 'subsystem' in data and isinstance(data, dict):
                subsystem = fileInfo[key]
                subsystemName = data['subsystem']
                self.extractedSubsystems[subsystemName] = subsystem

            if 'file' in data and isinstance(data, dict):
                fileName = data.pop('file')
                fileType = data.pop('type')
                if not fileType == 'yaml':
                    raise IncorrectFileTypeError("File type must be 'yaml'")
                loadedFile = self.__loadFile(fileName)
                self.__extractSubsystems(loadedFile)

        return self.extractedSubsystems

    def __getSubsystemDicts(self, subsystem, groupName):
        """
        Internally processes a subsystem, returning a dict of specific information.
        This information is typically used in the factories.
        """
        updatedSubsystem = {}
        # Loops through subsystem dict and finds nested dicts. When it finds one, dig deeper by running process again.
        # This specifically assures that it wont look deeper if it encounters 'groups' key
        for key in subsystem:
            if isinstance(subsystem[key], dict) and 'groups' not in subsystem:
                updatedValues = self.__getSubsystemDicts(subsystem[key], groupName)
                updatedSubsystem.update(updatedValues)

            # After searching, update new dict with values/dicts beyond 'groups' key
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
        return None

    def getSubsystems(self):
        """
        Returns a list of the subsystem names.
        """
        subsystems = list(self.subsystems.keys())
        return subsystems

    def getGroupDict(self, subsystem, groupName):
        """
        Retrieves important values from the config file and returns them as a dictionary.
        """
        rawSubsystem = self.getSubsystem(subsystem)
        subsystemDict = self.__getSubsystemDicts(rawSubsystem, groupName)
        return subsystemDict

    def checkCompatibility(self, compatString):
        """
        Checks compatibility of the component based on the compatString and the compatibility key in the config file.
        """
        compatString = [x.lower() for x in compatString]
        root = self.configCompat # This is the compatibility of the loaded file
        print(root)
        if root == "all" or "all" in compatString:
            return True
        for string in root:
            if string in compatString:
                return True
        return False

def findConfig():
    """
    Will determine the correct yml file for the robot.
    Please run 'echo (robotCfg.yml) > robotConfig' on the robot.
    This will tell the robot to use robotCfg file remove the () and use file name file.
    Files should be configs dir
    """
    configPath = os.path.dirname(__file__) + os.path.sep + ".." +os.path.sep + "configs" + os.path.sep
    home = str(Path.home()) + os.path.sep
    defaultConfig = "doof.yml"
    robotConfigFile = home + "robotConfig"
    

    if not os.path.isfile(robotConfigFile):
        log.error("Could not find %s. Using default", robotConfigFile)
        robotConfigFile = configPath + "default"
    try:
        file = open(robotConfigFile)
        configFileName = file.readline().strip()
        file.close()
        configFile = configPath + configFileName
        
        if os.path.isfile(configFile):
            log.info("Using %s config file", configFile)
            return configFileName, configPath
        log.error("No config? Can't find %s", configFile)
        log.error("Using default %s", defaultConfig)
    except Exception as e:
        log.error("Could not find %s", robotConfigFile)
        log.error(e)
        log.error("Please run `echo <robotcfg.yml> > ~/robotConcig` on the robot")
        log.error("Using default %s", defaultConfig)

    return defaultConfig, configPath


# if __name__ == "__main__":
#     mapper = ConfigMapper("doof.yml", "configs")
#     print("Subsystem driveTrain:", mapper.getSubsystem("driveTrain"))
    
#     print("driveTrain Motors")
#     pprint(mapper.getGroupDict("driveTrain", "motors"))
    
#     print("Shooter motors:")
#     pprint(mapper.getGroupDict("shooter", "motors", "loaderMotors"))

#     print("All motors:")
#     mapper.getGroupDict("/", "motors")
#     #print()
#     pprint(mapper.getGroupDict("/", "motors"))

#     print("CANTalonFXFollower motors:")
#     data = mapper.getTypesDict("/", "CANTalonFXFollower")
#     #print()
#     pprint(data)

#     compatTest = ["Dog", "all", "doof", "minibot", "DOOF"]
#     for item in compatTest:
#         compat = mapper.checkCompatibilty(item)
#         print(f"{item} is {compat}")

#     print("Subsystems: ", mapper.getSubsystems())
