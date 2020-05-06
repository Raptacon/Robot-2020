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
    Class to read a config file and parse its contents into a usable format to generate robot objects from
    factories.

    :param robot: Robot to set dictionary attributes to.

    :param config: If desired, specify a config to use. Default is listed in setup.json
    """

    def __init__(self, robot, config = None):

        root_dir = dirname(__file__) + os.path.sep + '..'

        base_data = {
            'setup_dir': root_dir + os.path.sep + 'configs' + os.path.sep + 'setup.json',
            'configs_dir': root_dir + os.path.sep + 'configs' + os.path.sep + 'robot' + os.path.sep
        }

        setup_data = self.__loadFile(base_data['setup_dir'])

        default_config = setup_data['default']
        factory_data = setup_data['factories']

        if config is None:
            log.warning("No config requested. Using default config: %s" %(default_config))
            loadedFile = self.__loadFile((base_data['configs_dir'] + default_config))
            configName = default_config

        elif '.json' not in config:
            raise TypeError(
                "Config requested '%s' is not a recognizable .json file. Use the file extention '.json'."
            )

        else:
            loadedFile = self.__loadFile((base_data['configs_dir'] + config))  
            configName = str(config)

        self.configName = configName
        self.robot = robot

        self.configCompat, self.subsystems = self.__getConfigInfo(loadedFile)

        # Loop through subsystems and pass data into function that generates objects from factories
        for subsystem_name, subsystem_data in self.subsystems.items():
            self.__generateFactoryObjects(factory_data, subsystem_name, subsystem_data)

    def __loadFile(self, directory):
        try:
            with open(directory) as file:
                loadedFile = json.load(file)
            return loadedFile
        except FileNotFoundError:
            raise

    def __getConfigInfo(self, configFile):
        """
        Takes data from a config file and extracts important pieces.
        """

        assert 'compatibility' in configFile, "Robot configs MUST have a 'compatibility' key."
        assert 'subsystems' in configFile, "Robot configs MUST have a 'subsystems' key."

        # Get config compatibility
        configCompat = configFile['compatibility']

        # Get subsystems
        subsystems = configFile['subsystems']

        # Return specific config info
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
        if not strict:
            log.error("Config requested in unreadable, likely due to the file being empty; unable to load.")
            configString = None
        else:
            raise SyntaxError(
                "Config requested in unreadable, likely due to the file being empty; unable to load. Aborting."
            )

    return configString

if __name__ == '__main__':

    mapper = ConfigMapper(None, config = findConfig())

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
