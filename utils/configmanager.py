from utils.hardwaremanager import HardwareObject
from importlib import import_module
import os
import json
from chardet import detect
from pathlib import Path
from typing import Optional, Union, get_type_hints


# Set constants
CONFIG_DIR = os.getcwd() + os.path.sep + "config" + os.path.sep
ROBOT_CFG_DIR = str(Path.home()) + os.path.sep + "RobotConfig"


class InitializeRobot:
    """Create robot objects.

    Sets hardware (and eventually software) attributes
    to a robot, used as injectables for components to use.
    Also disables incompatable components for the loaded
    robot.

    :param base_cls: Robot class object to set attributes
    to.

    :param cfg_file: Specify a config file to use. If not
    specified, attempt to find the config name on the robot
    (run `echo <cfg_name> RobotConfig` to set a config
    directly on the robot).

    :param robot_name: Specify a robot name to use to
    enable/disable components. If not specified, use
    the name of the config file (excluding extentions).

    :param generate_objects: If desired, disable the
    creation of injecable dictionaries for the robot.
    Defaults to True. THIS SHOULD ONLY BE USED FOR
    DEBUGGING.
    """

    def __init__(self, base_cls, cfg_file: Optional[str]=None,
                 robot_name: Optional[str]=None, 
                 generate_objects: Optional[bool]=True
                ):

        self.robot_cls = base_cls
        self.log = base_cls.logger

        config = cfg_file if cfg_file is not None else self._find_config()

        self.log.info(f"Using config {config!r}")
        config_data = self._load(config)

        if generate_objects:
            self._generate_hardware_objects(config_data)
        self._cleanup_components()

        _name = config.split('.')[0]
        self.robot_name = robot_name if robot_name is not None else _name

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

    def _load(self, cfg_name) -> Union[dict, list]:
        """
        Load a JSON file.

        :param cfg_name: Name of JSON config file to load.

        NOTE: This automatically fills in the directory
        with the config directory, this DOES NOT accept
        full directories as an argument.
        """

        cfg_dir = CONFIG_DIR + cfg_name
        with open(cfg_dir) as file:
            return json.load(file)

    def _cleanup_components(self):
        """
        Remove incompatable components from the robot class.
        """

        cls = type(self.robot_cls)

        #
        # HACK: to allow `get_type_hints` to work
        #       with pybind11_bultins.
        #
        # NOTE: This is the same hack used in
        #       MagicRobot.
        #
        class FakeModule:
            pass

        import sys

        sys.modules["pybind11_builtins"] = FakeModule()

        annotations = get_type_hints(cls)
        bad_components = []

        for cname, c in annotations.items():
            compat_robots = getattr(c, "robot", None)
            if not compat_robots:

                #
                # XXX: Should this be a warning and enable the
                #      component by default?
                #
                #      Or, we could seperate robot components into their
                #      own directories (i.e. components\doof\component.py)
                #      and use inspect.getsourcefile(c) to check if the
                #      component belongs to a specific robot (then no need
                #      for a `self.robot_name` attribute at all).
                #

                raise AttributeError(
                    f"Component {cname} ({c}) is missing a 'robot'"
                    " attribute; component cannot be created."
                )
            if self.robot_name in compat_robots or "all" in compat_robots:
                continue
            else:
                bad_components.append(cname)

        for bad_comp in bad_components:
            cls.logger.info(f"Removing component {bad_comp!r}")
            del annotations[bad_comp]

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
