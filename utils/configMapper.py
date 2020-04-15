import yaml
import logging as log
import os
from pathlib import Path

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
        except:
            raise AttributeError(
                "No compatibility key found in config file. Unable to bind correct components."
            )

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
                try:
                    fileType = data.pop('type')
                except:
                    raise FileNotFoundError(
                        "Unable to load file '%s': No file type found." %(key)
                        )
                if not fileType == 'yaml':
                    raise FileNotFoundError(
                        "Unable to load file '%s': File type must be 'yaml'. File type found: %s" %(key, fileType)
                    )
                loadedFile = self.__loadFile(fileName)
                self.__extractSubsystems(loadedFile)

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
            if 'groups' in subsystem:
                if groupName in subsystem["groups"]:
                    updatedSubsystem.update(subsystem)

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
        root = [self.configCompat] # This is the compatibility of the loaded file
        if "all" in root or "all" in compatString:
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

if __name__ == '__main__':
    """
    Standard testing for elements of the config. To run this, simply run the python file
    by itself.
    """
    configFile, configPath = findConfig()
    print('')
    print("Config file used:", configFile)
    print("Config path:", configPath)
    print('')

    mapper = ConfigMapper(configFile, configPath)

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
    print("Is %s compatible? %s <--- (This should say 'True')" %(exampleCompatString, isCompatible))
