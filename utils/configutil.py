from utils.hardwareutil import generate_hardware_objects
import os
import sys
import json
import wpilib
from chardet import detect
from pathlib import Path
from warnings import warn
from typing import Optional, Union, get_type_hints


__all__ = ["parse_robot_args", "InitializeRobot"]


def parse_robot_args():
    """Parse robot arguments.

    As of now, this only checks for a `--config`
    flag and determines a configuration file to
    use. To set a configuration via commandline,
    use this command:

        py robot.py {sim | deploy} --config {cfg_name.json}
    """

    args = sys.argv
    if "--config" in args:
        cfg_flag = args[args.index("--config")]
        cfg_name = args[args.index("--config") + 1]
        InitializeRobot.__configuration__ = cfg_name
        # must remove additional args, or wpilib.run will complain
        args.remove(cfg_flag)
        args.remove(cfg_name)


class InitializeRobot:
    """Create robot objects.

    Sets hardware (and eventually software) attributes
    to a robot, used as injectables for components to use.
    Also disables incompatable components for the loaded
    robot.

    :param base_cls: Robot class object to set attributes
    to.

    :param default_config: Configuration to default to if
    none is specified.
    """

    # used if config specified as arg in cmdline
    __configuration__ = None

    def __init__(self, base_cls: wpilib.RobotBase,
                 default_config: str=None):

        self.robot_cls = base_cls

        if self.__configuration__:
            config = self.__configuration__
            self.robot_cls.logger.info(f"Using config {config!r}")
        else:
            msg = ("no config specified in commandline, "
                   f"using default: {default_config!r}")
            self.robot_cls.logger.warning(msg)
            config = default_config

        generate_hardware_objects(self.robot_cls, self._load(config))
        self._cleanup_components()

        self.robot_name = config.split('.')[0]

    def _load(self, cfg_name) -> Union[dict, list]:
        """
        Load a JSON file.

        :param cfg_name: Name of JSON config file to load.

        NOTE: This automatically fills in the directory
        with the config directory, this DOES NOT accept
        full directories as an argument.
        """

        cfg_dir = os.getcwd() + os.path.sep + "config" + os.path.sep + cfg_name
        with open(cfg_dir) as file:
            return json.load(file)

    def _cleanup_components(self):
        """
        Remove incompatable components from the robot class.
        """

        # this allows us to access __annotations__ from
        # the instance rather than the class itself
        cls = type(self.robot_cls)

        #
        # HACK: to allow `get_type_hints` to work
        #       with pybind11_bultins.
        #
        class FakeModule:
            pass

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
