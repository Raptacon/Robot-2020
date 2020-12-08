import wpilib
import os
import json
import sys
import inspect

import ctre
import rev
import navx


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


# Define custom errors
class DuplicateTypeError(AttributeError):
    """
    Raised when two `__type__` keys in two different constructors
    have the same value.
    """


class NoConstructorError(ValueError):
    """
    Raised when a type is missing a binded constructor.
    """


class NoTypeFoundError(AttributeError):
    """
    Raised when no `__type__` attribute is found in a constructor.
    """


class MissingRequiredKeysError(AttributeError):
    """
    Raised when keys listed in `__required_keys__` are missing
    in the desc passed to the constructor.
    """

#
# Mapping to hold Python objects that
# construct usable hardware objects
# NOTE this is implicitly filled in
#      by the `_PyHardwareObject` class
#
_OBJECT_MAPPING = {}


def generate_hardware_objects(robot_cls: wpilib.RobotBase, *, hardware_cfg: dict):
    """Generate hardware objects for a robot.

    This sets injectable dictionaries with hardware attributes to the robot
    in the form of `groupName_subsystemName` (i.e., `motors_driveTrain`)
    to be used in components. Example hardware configuration below:

        "motors": {
            "driveTrain": {
                "rightMotor": {
                    "channel": 30,
                    "type": "CANTalonFX",
                    "inverted": true,
                    "currentLimits": {
                        "triggerThresholdCurrent": 60,
                        "triggerThresholdTime": 50,
                        "currentLimit": 40
                    }
                },
                "rightFollower": {
                    ...

    ...and example usage:

        class DriveTrain:

            motors_driveTrain: dict

            def on_enable(self):
                self.rightMotor = self.motors_driveTrain["rightMotor"]

    :param robot_cls: Base robot class to set injectable dictionaries to.

    :param hardware_cfg: A dictionary hardware configuration to use to
    generate objects.
    """

    log = robot_cls.logger

    def new_hardware_object(desc):
        """Generate a new hardware object.

        Search through registered classes that inherit from `_PyHardwareObject`
        to find a which object matches the type specified in the `desc` provided.

        :param desc: Object description
        """

        #
        # XXX: Most of this stuff is just error checking to give
        #      a meaningful error if the user sets up an object
        #      incorrectly. Same idea applies for `_PyHardwareObject`
        #

        typ = desc.pop("type", None)
        c = _OBJECT_MAPPING.get(typ, None)
        r = getattr(c, "__required_keys__", None)

        # assert type key exists - otherwise,
        # no object can be created
        if typ is None:
            _msg = "missing 'type' key in description. desc is {}"
            msg = _msg.format(desc)
            raise AttributeError(msg)

        # assert type given actually has a
        # binded constructor object
        if c is None:
            _msg = "object type {!r} is missing a constructor object"
            msg = _msg.format(typ)
            raise NoConstructorError(msg)

        # check required attributes
        if r is not None:
            is_iterable = hasattr(r, "__iter__")
            is_string = type(r).__name__ == "str"
            if not (is_iterable or is_string):
                _msg = ("__required_keys__ must be an iterable or a "
                        "string; found {} in constructor {!r} ({})")
                msg = _msg.format(type(r).__name__, c.__name__, c)
                raise TypeError(msg)
            # define this here to avoid repeating it
            _msg = ("required attriute {!r} missing in description "
                    "passed into constructor {!r} ({}). desc is {}")
            if is_iterable:
                for attr in r:
                    if attr not in desc:
                        msg = _msg.format(attr, c.__name__, c, desc)
                        raise MissingRequiredKeysError(msg)
            if is_string:
                if r not in desc:
                    msg = _msg.format(r, c.__name__, c, desc)
                    raise MissingRequiredKeysError(msg)

        log.info(f"creating {c} object with desc {desc}")
        # this allows for empty classes (such as `Compressor`)
        return c(desc) if bool(desc) else c()

    total_items = 0
    for general_type, all_objects in hardware_cfg.items():
        for subsystem_name, subsystem_items in all_objects.items():
            for item_name, item_desc in subsystem_items.items():
                subsystem_items[item_name] = new_hardware_object(item_desc)
                total_items += 1
            group_subsystem = "_".join([general_type, subsystem_name])
            setattr(robot_cls, group_subsystem, subsystem_items)
            log.info(
                f"created {len(subsystem_items)} item(s) into {group_subsystem}"
            )
    log.info(f"created {total_items} total items")


class _Identifier:
    """
    Indicate that the child class acts only as an identifier
    and provides no actual implimentation when subclassed, only
    internal modifiers and checks.
    """

    # assert all attributes are private/dunder/sunder,
    # as to not be used in any child classes
    def __init_subclass__(cls):
        for member in inspect.getmembers(cls):
            name = member[0]
            obj = member[1]
            if not name.startswith("_"):
                _msg = ("_Identifier object {!r} has "
                        "a public attribute {!r} ({})")
                msg = _msg.format(cls, name, obj)
                raise AttributeError(msg)


class _PyHardwareObject(_Identifier):
    """Base hardware class.

    All hardware constructor objects should inherit from
    this class. This class should not be instantiated by
    itself.
    """

    # this only exists to prevent direct instantiation
    def __init__(self, *args, **kwargs):
        if self is _PyHardwareObject:
            raise TypeError(
                "do not instantiate '_PyHardwareObject' directly"
            )

    def __init_subclass__(cls):
        """Initialize hardware constructor objects.

        This exists to assert hardware constructors have
        the appropriate attributes and to register
        the object and its type to `_OBJECT_MAPPING`
        Supported custom attributes include `__type__`
        and `__required_keys__`.
        """

        _type = getattr(cls, "__type__", None)

        # assert __type__ exists
        if _type is None:
            _msg = ("constructor {!r} ({}) missing '__type__' "
                    "attribute, unable to map any types")
            msg = _msg.format(cls.__name__, cls)
            raise NoTypeFoundError(msg)

        # assert __type__ is str
        elif not isinstance(_type, str):
            _msg = ("'__type__' attribute in constructor {!r} "
                    "({}) is of an incorrect type: expected "
                    "str, found {}")
            msg = _msg.format(cls.__name__, cls, type(_type).__name__)
            raise TypeError(msg)

        # assert only `desc` arg in constructor `__init__`,
        # this will cause problems later if this isn't checked
        _constructor_args = inspect.getfullargspec(cls).args
        if len(_constructor_args) > 2:
            _msg = ("too many positional arguments in constructor "
                    "{!r} ({}), unable to create hardware objects "
                    "correctly (expected 2 positional arguments, "
                    "found {}. args: {})")
            msg = _msg.format(cls.__name__, cls,
                              len(_constructor_args),
                              _constructor_args)
            raise ValueError(msg)

        # assert no duplicate __type__ values
        if _type in _OBJECT_MAPPING:
            _msg = ("'__type__' attribute of constructor {!r} ({}) "
                    "has name {!r}, which was already defined "
                    "in constructor {!r} ({})")
            msg = _msg.format(cls.__name__, cls, _type,
                              _OBJECT_MAPPING.get(_type).__name__,
                              _OBJECT_MAPPING.get(_type))
            raise DuplicateTypeError(msg)

        info_msg = f"adding type {_type!r} with constructor {cls}"
        print(info_msg)
        # update mapping with constructor object
        _OBJECT_MAPPING.update({_type: cls})


class CANTalonSRX(_PyHardwareObject, ctre.WPI_TalonSRX):
    """
    Create a WPI_TalonSRX object.

    :param desc: Object description
    """

    __type__ = "CANTalonSRX"
    __required_keys__ = ('channel',)
    
    def __init__(self, desc):

        # Setup conditional variables
        self._has_pid = False

        # Define constructor variables
        channel = desc["channel"]

        #
        # Initialize parent class
        #
        # NOTE: We can't use `super()` here because we also inherit
        #       from _PyHardwareObject, but we need to still inherit the
        #       other base to give the below line a valid
        #       ctre.WPI_TalonSRX object (that's the `self` param)
        #
        ctre.WPI_TalonSRX.__init__(self, channel)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            #
            # TODO: test the .follow function, as well as this
            # NOTE: `ctre.WPI_TalonSRX` needed because
            #       we override the default `set`
            #
            ctre.WPI_TalonSRX.set(self,
                mode=ctre.ControlMode.Follower,
                value=desc["masterChannel"]
            )
        if "pid" in desc:
            self._has_pid = True
            self.__setupPID(desc["pid"])
        if "currentLimits" in desc:
            self.__setCurrentLimits(desc["currentLimits"])
        if "inverted" in desc:
            self.setInverted(desc["inverted"])

    def __setupPID(self, pid_desc):
        """
        Setup PID for a TalonSRX motor.
        """

        control_type = pid_desc["controlType"]
        self.control_type = getattr(ctre.ControlMode, control_type)

        feedback = ctre.FeedbackDevice(pid_desc['feedbackDevice'])
        self.configSelectedFeedbackSensor(feedback, 0, 10)
        self.setSensorPhase(pid_desc['sensorPhase'])
        self.kPreScale = pid_desc['kPreScale']

        # Set the peak outputs, nominal outputs, and deadband
        self.configNominalOutputForward(0, 10)
        self.configNominalOutputReverse(0, 10)
        self.configPeakOutputForward(1, 10)
        self.configPeakOutputReverse(-1, 10)
        self.configVelocityMeasurementPeriod(
            ctre.VelocityMeasPeriod(1), 10)

        # Configure PID(F) values
        self.config_kP(0, pid_desc['kP'], 10)
        self.config_kI(0, pid_desc['kI'], 10)
        self.config_kD(0, pid_desc['kD'], 10)
        self.config_kF(0, pid_desc['kF'], 10)

    def __setCurrentLimits(self, cl_desc):
        """
        Set current limits for a TalonSRX motor.
        """

        absMax = cl_desc['absMax']
        absMaxTimeMs = cl_desc['absMaxTimeMs']
        nominalMaxCurrent = cl_desc['maxNominal']
        self.configPeakCurrentLimit(absMax, 10)
        self.configPeakCurrentDuration(absMaxTimeMs, 10)
        self.configContinuousCurrentLimit(nominalMaxCurrent, 10)
        self.enableCurrentLimit(True)

    def set(self, speed):
        """
        Set the speed for a TalonSRX motor.
        """
        # XXX why do we return on set? Caiden?
        if self._has_pid:
            return ctre.WPI_TalonSRX.set(self, self.control_type, speed * self.kPreScale)
        else:
            return ctre.WPI_TalonSRX.set(self, speed)


class CANTalonFX(_PyHardwareObject, ctre.WPI_TalonFX):
    """
    Create a WPI_TalonFX object.

    :param desc: Object description
    """

    __type__ = "CANTalonFX"
    __required_keys__ = ('channel',)

    def __init__(self, desc):

        # Setup conditional variables
        self._has_pid = False

        # Define constructor variables
        channel = desc["channel"]

        # Initialize parent class
        ctre.WPI_TalonFX.__init__(self, channel)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            ctre.WPI_TalonFX.set(self,
                mode=ctre.TalonFXControlMode.Follower,
                value=desc["masterChannel"]
            )
        # Instantiate other pieces of the motor
        if "pid" in desc:
            self._has_pid = True
            self.__setupPID(desc["pid"])
        if "currentLimits" in desc:
            self.__setCurrentLimits(desc["currentLimits"])
        if "inverted" in desc:
            self.setInverted(desc["inverted"])

    def __setupPID(self, pid_desc):
        """
        Setup PID for a TalonFX motor.
        """

        control_type = pid_desc["controlType"]
        self.control_type = getattr(ctre.TalonFXControlMode, control_type)

        feedback = ctre.FeedbackDevice(pid_desc['feedbackDevice'])
        self.configSelectedFeedbackSensor(feedback, 0, 10)
        self.setSensorPhase(pid_desc['sensorPhase'])
        self.kPreScale = pid_desc['kPreScale']

        # Set the peak outputs, nominal outputs, and deadband
        self.configNominalOutputForward(0, 10)
        self.configNominalOutputReverse(0, 10)
        self.configPeakOutputForward(1, 10)
        self.configPeakOutputReverse(-1, 10)
        self.configVelocityMeasurementPeriod(
            ctre.VelocityMeasPeriod(1), 10)

        # Configure PID(F) values
        self.config_kP(0, pid_desc['kP'], 10)
        self.config_kI(0, pid_desc['kI'], 10)
        self.config_kD(0, pid_desc['kD'], 10)
        self.config_kF(0, pid_desc['kF'], 10)

    def __setCurrentLimits(self, cl_desc):
        """
        Set current limits for a TalonFX motor.
        """

        currentLimit = cl_desc['currentLimit']
        triggerThresholdCurrent = cl_desc['triggerThresholdCurrent']
        triggerThresholdTime = cl_desc['triggerThresholdTime']
        args = [True, currentLimit,
                triggerThresholdCurrent,
                triggerThresholdTime]
        statorCurrentConfig = ctre.StatorCurrentLimitConfiguration(*args)
        supplyCurrentConfig = ctre.SupplyCurrentLimitConfiguration(*args)
        self.configStatorCurrentLimit(statorCurrentConfig)
        self.configSupplyCurrentLimit(supplyCurrentConfig)

    def set(self, speed):
        """
        Set the speed for a TalonFX motor.
        """

        if self._has_pid:
            return ctre.WPI_TalonFX.set(self, self.control_type, speed * self.kPreScale)
        else:
            return ctre.WPI_TalonFX.set(self, speed)


class CANSparkMax(_PyHardwareObject, rev.CANSparkMax):
    """
    Create a CANSparkMax object.

    :param desc: Object description
    """

    __type__ = "CANSparkMax"
    __required_keys__ = ('channel', 'motorType',)

    # Followers require objects, not channels
    # All SparkMax motors MUST be registered to be used
    # as a follower
    motors = {}

    def __init__(self, desc):

        # Setup conditional variables
        self._coasting = False
        self._has_pid = False

        # Setup constructor variables
        channel = desc["channel"]
        motor_type = getattr(rev.MotorType, desc["motorType"])

        # Initialize parent class
        rev.CANSparkMax.__init__(self, channel, motor_type)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            rev.CANSparkMax.follow(self,
                self.motors.get(str(desc['masterChannel'])),
                desc['inverted']
            )
        if "pid" in desc:
            self._has_pid = True
            self.__setupPID(desc["pid"])
        if "currentLimits" in desc:
            self.__setCurrentLimits(desc["currentLimits"])
        if "inverted" in desc:
            self.setInverted(desc["inverted"])

        self.motors[channel] = self

    def __setupPID(self, pid_desc):
        """
        Setup PID for a SparkMax motor.
        """

        self.control_type = None
        self.init_control_type = pid_desc["controlType"]
        self.__set_control_type(self.init_control_type)

        # XXX Why are we defining encoder? It's never used.
        self.encoder = self.getEncoder()
        self.kPreScale = pid_desc['kPreScale']  # Multiplier for speed
        self.feedbackDevice = pid_desc["feedbackDevice"]
        self.PIDController = self.getPIDController()

        # Configure PID(F) values
        self.PIDController.setP(pid_desc['kP'], self.feedbackDevice)
        self.PIDController.setI(pid_desc['kI'], self.feedbackDevice)
        self.PIDController.setD(pid_desc['kD'], self.feedbackDevice)
        self.PIDController.setFF(pid_desc['kF'], self.feedbackDevice)

        # XXX If this doesn't work why is it still here?
        if 'IdleBrake' in pid_desc:
            self.setIdleMode(rev.IdleMode.kBrake)
        else:
            self.setIdleMode(rev.IdleMode.kCoast)

        # Configures output range - that's what SparkMax motors accept
        self.PIDController.setOutputRange(-1, 1, self.feedbackDevice)
        self.PIDController.setReference(
            0, self.control_type, self.feedbackDevice)

    def __setCurrentLimits(self, cl_desc):
        """
        Set current limits for a SparkMax motor.
        """

        freeLimit = cl_desc['freeLimit']
        stallLimit = cl_desc['stallLimit']
        limitRPM = cl_desc['stallLimitRPM']
        secondaryLimit = cl_desc['secondaryLimit']
        self.setSecondaryCurrentLimit(secondaryLimit)
        self.setSmartCurrentLimit(
            stallLimit, freeLimit, limitRPM)

    # Coasting hacks necessary because the REV API doesn't
    # provide the appropriate means to coast the way we need to
    def __set_control_type(self, control_type: str):
        """
        Dynamically change the control type.
        """

        self.control_type = getattr(rev.ControlType, control_type)

    def __coast(self):
        """
        Changes the control type to "Duty Cycle" and
        sets the speed to 0.
        """

        if self._coasting:
            return
        self._coasting = True
        self.__set_control_type("kDutyCycle")
        self.PIDController.setReference(
            0, self.control_type, self.feedbackDevice)

    def __stop_coast(self):
        """
        Restores the previous control type and
        stops the motor from coasting.
        """

        if self._coasting:
            self.control_type = self.init_control_type
        self._coasting = False

    def set(self, speed, coast=True):
        """
        Set the speed for a SparkMax motor.
        """

        if self._has_pid:
            self.__coast() if coast and speed == 0 else self.__stop_coast()
            return self.PIDController.setReference(speed * self.kPreScale, 
                                                   self.control_type,
                                                   self.feedbackDevice)
        return rev.CANSparkMax.set(self, speed)


class Compressor(_PyHardwareObject, wpilib.Compressor):
    """
    Create a Compressor object.
    """

    __type__ = "compressor"
    __required_keys__ = ()


class Solenoid(_PyHardwareObject, wpilib.Solenoid):
    """
    Create a Solenoid object.

    :param desc: Object description
    """

    __type__ = "solenoid"
    __required_keys__ = ('channel',)

    def __init__(self, desc):
        pcm = 0
        if "pcm" in desc:
            pcm = desc["pcm"]
        wpilib.Solenoid.__init__(self, pcm, desc["channel"])


class DoubleSolenoid(_PyHardwareObject, wpilib.DoubleSolenoid):
    """
    Create a DoubleSolenoid object.

    :param desc: Object description
    """

    __type__ = "doubleSolenoid"
    __required_keys__ = ('channel',)

    def __init__(self, desc):
        pcm = 0
        if "pcm" in desc:
            pcm = desc["pcm"]
        wpilib.DoubleSolenoid.__init__(self, pcm,
                         desc["channel"]["forward"],
                         desc["channel"]["reverse"])
        if "default" in desc:
            default_pos = {
                "kOff": 0, "kForward": 1, "kReverse": 2
            }[desc["default"]]
            self.set(wpilib.DoubleSolenoid.Value(default_pos))


class NavX(_PyHardwareObject, navx.AHRS):
    """
    Create a navx.AHRS object.

    :param desc: Object description
    """

    __type__ = "navx"
    __required_keys__ = ('method',)

    def __init__(self, desc):
        method = desc["method"]
        _navx = navx.AHRS
        if method == "spi":
            _navx.create_spi()
        elif method == "i2c":
            _navx.create_i2c()


class Breaksensor(_PyHardwareObject, wpilib.DigitalInput):
    """
    Create a DigitalInput object.

    :param desc: Object description
    """

    __type__ = "RIODigitalIn"
    __required_keys__ = ('channel',)

    def __init__(self, desc):
        channel = desc["channel"]
        wpilib.DigitalInput.__init__(self, channel)


class XboxController(_PyHardwareObject, wpilib.XboxController):
    """
    Create an XboxController object.

    :param desc: Object description
    """

    __type__ = "XboxController"
    __required_keys__ = ('channel',)

    def __init__(self, desc):
        channel = desc["channel"]
        wpilib.XboxController.__init__(self, channel)



class HardwareRegistry:

    __objs__ = {}

    def __init__(self, robot: wpilib.RobotBase, cfg_obj: ConfigManager):
        self.robot = robot
        self.cfg_obj = cfg_obj
        self.log = self.robot.logger

    def __enter__(self):
        return self.register

    def __exit__(self, *traceback_args):
        pass

    @classmethod
    def register(cls, typ_name, obj):
        cls.__objs__[typ_name] = obj

    def new_hardware_object(self, desc: dict):
        _type = desc.pop("type")
        c = self.__objs__.get(_type, None)

        if not isinstance(c, _PyHardwareObject):
            pass

        return c(desc) if bool(desc) else c()

    def create_objs(self):
        total_items = 0
        for general_type, all_objects in self.cfg_obj.data.items():
            for subsystem_name, subsystem_items in all_objects.items():
                for item_name, item_desc in subsystem_items.items():
                    subsystem_items[item_name] = self.new_hardware_object(item_desc)
                    total_items += 1
                group_subsystem = "_".join([general_type, subsystem_name])
                setattr(self.robot, group_subsystem, subsystem_items)
                self.log.info(
                    f"created {len(subsystem_items)} item(s) into {group_subsystem}"
                )
        self.log.info(f"created {total_items} total items")
            
