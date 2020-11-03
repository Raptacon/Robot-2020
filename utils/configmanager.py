from utils.hardwaremanager import HardwareObject
from importlib import import_module
from warnings import warn
import os
import json
from chardet import detect
from pathlib import Path
from typing import Optional


# Set global variables
sep = os.path.sep
cwd = os.getcwd()

# Set constants
CONFIG_DIR = cwd + sep + "config" + sep
# NOTE we use `Path.home()` here because when we
#      echo a robot config to use, it goes into the
#      home directory on the robot.
ROBOT_CFG_DIR = Path.home() + sep + "RobotConfig"


class InitializeRobot:
    """Create robot objects.

    Sets hardware (and eventually software) attributes
    to a robot, used as injectables for components to use.

    :param base_cls: Robot class object to set attributes
    to.

    :param cfg_file: Specify a config file to use. If not
    specified, attempt to find the config name on the robot
    (run `echo <cfg_name> RobotConfig` to set a config
    directly on the robot).
    """

    def __init__(self, base_cls, cfg_file: Optional[str]=None):

        self.robot_cls = base_cls
        self.log = base_cls.logger

        config = cfg_file if cfg_file is not None else self._find_config()

        self.log.info(f"Using config {config!r}")
        config_data = self._load(config)

        self._generate_hardware_objects(config_data)

        # Used to disable components in createObjects
        self.robot_name = config.split('.')[0]

    def _find_config(self) -> str:
        """
        Find an echo'd config on the robot, read it, and open
        it appropriately.
        """

        default_config = "doof.json"
        try:
            with open(ROBOT_CFG_DIR, 'rb') as rf:
                raw_data = rf.readline().strip()
            encoding_type = ((detect(raw_data))['encoding']).lower()
            with open(ROBOT_CFG_DIR, 'r', encoding=encoding_type) as file:
                configString = file.readline().strip()
            self.log.info(f"Config found in {ROBOT_CFG_DIR}")
        except FileNotFoundError:
            self.log.error(f"{ROBOT_CFG_DIR} could not be found.")
            configString = default_config
        return configString

    def _load(self, cfg_name):
        """
        Load a JSON file.

        :param cfg_name: Name of JSON config file to load.

        NOTE: This automatically fills in the directory
        with the config directory, this DOES NOT accept
        full directories as an argument.
        """

        cfg_dir = CONFIG_DIR + cfg_name
        return json.load(cfg_dir)

    def _generate_hardware_objects(self, robot_hardware: dict):
        """
        Generate injectable dictionaries for the robot.
        """

        for general_type, all_objects in robot_hardware.items():
            for subsystem_name, subsystem_items in all_objects.items():
                for item_name, item_desc in subsystem_items.items():
                    subsystem_items[item_name] = HardwareObject(item_desc)
                group_subsystem = "_".join([general_type, subsystem_name])
                setattr(self.robot_cls, group_subsystem, subsystem_items)
