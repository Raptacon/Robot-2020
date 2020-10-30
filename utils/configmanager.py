from utils.filemanager import FileManager
from utils.hardwaremanager import HardwareObject
from importlib import import_module
from warnings import warn
import os
from pathlib import Path
from chardet import detect
from typing import Optional


# Set global variables
sep = os.path.sep
cwd = os.getcwd()
load = FileManager.load

# Set constants
CONFIGS = cwd + sep + "config" + sep
ROBOT_CONFIGS = CONFIGS + sep
HARDWARE_CONFIG = ".config.hardware.json"
SOFTWARE_CONFIG = ".config.software.json"

# XXX should this stuff be in a config file?
# SETUP_CONFIG = CONFIGS + ".setup.json"
# default_config = load(SETUP_CONFIG)["default"]
DEFAULT = ROBOT_CONFIGS + "doof" + sep

class InitializeRobot:

    def __init__(self, base_cls, robot: Optional[str] = None):

        self.robot_cls = base_cls
        if not robot:
            warn(
                f"No robot specified. Using default robot: {DEFAULT}", Warning
            )
            # FIXME make variable, don't define robot as "doof" here
            robot = "doof"
            config_dir = DEFAULT
        else:
            config_dir = ROBOT_CONFIGS + robot + sep

        hardware_dir = config_dir + HARDWARE_CONFIG
        print("loading dir", hardware_dir)
        hardware_config = load(hardware_dir)
        # software_dir = ROBOT_CONFIGS + config + sep + SOFTWARE_CONFIG
        # print("loading dir", software_dir)
        # software_config = load(software_dir)

        self._generate_hardware_objects(hardware_config)
        # self._generate_software_params(software_config)

        # Used to disable components in createObjects
        self.config = robot

    def _generate_hardware_objects(self, robot_hardware: dict):
        """
        Generate injectable dictionaries for the robot.
        """

        for general_type, all_objects in robot_hardware.items():
            for subsystem_name, subsystem_items in all_objects.items():
                for item_name, item_desc in subsystem_items.items():
                    subsystem_items[item_name] = HardwareObject(item_desc)
                group_subsystem = "_".join([general_type, subsystem_name])
                self._set_injectable(group_subsystem, subsystem_items)

    def _generate_software_params(self, robot_software: dict):
        """
        Generate injectable paramaters that alter the robots behavior.
        """

        for var, value in robot_software.items():
            self._set_injectable(var, value)

    def _set_injectable(self, name, value):
        """
        Set a value to the robot to be used as an injectable.
        """

        setattr(self.robot_cls, name, value)
