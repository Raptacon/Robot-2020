import os
import sys
import json
import wpilib
from typing import Union, get_type_hints
from warnings import warn

# eh, kind of iffy on this import
from utils.hardwareutil import generate_hardware_objects


__all__ = ["InitializeRobot"]


class _ArgumentHelper:

    def __init_subclass__(cls):
        """Parse commandline args at compile time.

        Ultimately this only exists to parse arguments
        BEFORE `wpilib.run` is called.
        """

        flag_pairs = []
        cmdargs = sys.argv
        for arg in cmdargs:
            if arg.startswith('-'):
                # kind of brute-forcing this...
                # TODO find a better way to get flags/args
                flag = cmdargs[cmdargs.index(arg)]
                param = cmdargs[cmdargs.index(arg) + 1]
                flag_pairs.append((flag, param))
                cmdargs.remove(flag)
                cmdargs.remove(param)

        for flag_pair in flag_pairs:
            flag = flag_pair[0]
            arg = flag_pair[1]
            # again, somewhat brute-forcing this
            if flag == "--config":
                cls.__config__ = arg


class InitializeRobot(_ArgumentHelper):
    """
    Initialize a robot class.
    """

    __config__ = None

    def __init__(self, robot_cls: wpilib.RobotBase, default_cfg: str=None):

        if self.__config__ is None:
            robot_cls.logger.warning("No config specified")
            self.__config__ = default_cfg

        robot_cls.logger.info(f"Using config: {self.__config__!r}")

        config_name = self.__config__.strip(".json")
        config_data = self._load(self.__config__)

        generate_hardware_objects(robot_cls, config_data)
        self._cleanup_components(robot_cls, config_name)

    def _load(self, cfg_name):
        """
        Load a JSON config.
        """

        filedir = os.getcwd() + os.path.sep + "config" + os.path.sep + cfg_name
        with open(filedir) as file:
            return json.load(file)

    def _cleanup_components(self, robot_cls, key: str):
        """Remove incompatable components.

        If multiple robots are being used and the components
        for these robots are defined in one robot class, this
        fucntion eill remove any incompatable components from
        the robot class. All components MUST have a `robot`
        attribute to determine what robot they belong to.

        :param robot_cls: Robot class to check components
        for (i.e. `MyRobot`).

        :param key: Key used to determine what components to use.
        If a component doesn't have this key in it's `robot`
        attribute, it is removed and not used in the robot.
        This is typically (and should be) the name of the config
        file selected.
        """

        # this allows us to access __annotations__ from
        # the instance rather than the class itself
        cls = type(robot_cls)

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
            if key in compat_robots or "all" in compat_robots:
                continue
            else:
                bad_components.append(cname)

        for bad_comp in bad_components:
            robot_cls.logger.info(f"Removing component {bad_comp!r}")
            del annotations[bad_comp]
