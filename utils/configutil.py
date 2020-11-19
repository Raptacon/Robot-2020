import os
import sys
import json
import wpilib  # only for annotations


__all__ = ["ConfigManager"]


class _ArgumentHelper:
    """
    Help handle commandline arguments.
    """

    def __init_subclass__(cls):
        """Parse commandline args at compile time.

        Ultimately, this only exists to parse arguments
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


class ConfigManager(_ArgumentHelper):
    """Robot configuration object.

    Store configuration information in an object. This
    includes name of the config file (without extentions)
    and the loaded data within the config file.

    :param robot_cls: Base robot class, used for logging
    purposes.

    :param default: Default config to be used if
    none is specified via commandline.
    """

    __config__ = None

    def __init__(self, robot_cls: wpilib.RobotBase, *, default: str):

        log = robot_cls.logger

        if self.__config__ is None:
            log.warning("No config specified, using default")
            self.__config__ = default

        if not self._format_check(self.__config__):
            raise SyntaxError(
                f"config {self.__config__!r} must be "
                 "a valid JSON file (include '.json')"
            )

        log.info(f"Using config {self.__config__!r}")
        self._data = self._load(self.__config__)

    def _format_check(self, string):
        """
        Assert config name has a valid JSON extention.
        """

        return string[-5:] == ".json"

    def _load(self, string):
        """
        Load config data.
        """

        cfgsdir = os.getcwd() + os.path.sep + "config" + os.path.sep
        filedir = cfgsdir + self.__config__

        with open(filedir) as file:
            return json.load(file)

    @property
    def name(self):
        """Get the name of the config file.

        This is usually the robot name, and is used for
        checking and disabling components.
        """

        return self.__config__.strip(".json")

    @property
    def data(self):
        """
        Get the data of the config file.
        """

        return self._data
