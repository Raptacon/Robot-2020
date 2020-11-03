import ctre
import rev
import navx
import wpilib

# NOTE this is only used for Xbox controllers
import time
import threading
# from utils.buttonmanager import Button, ButtonEvent


__all__ = ["HardwareObject"]


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


# Begin API
# NOTE `HardwareObject` is the only public class
# TODO switch print statements to log or something else
class HardwareObject:  # maybe rename to `CreateHardwareObject`
    """Public hardware constructor class.

    Returns an initilized object of a type
    specified in the `desc` param.

    :param desc: Object description.
    """

    # holder mapping for types and constructor objects
    __objs__ = {}

    def __new__(cls, desc: dict):

        typ = desc.pop("type", None)
        c = cls.__objs__.get(typ, None)
        r = getattr(c, "__required_keys__", None)

        # assert type key exists - otherwise,
        # no object can be created
        if typ is None:
            _msg = ("missing 'type' key in description. "
                    "desc is {}")
            msg = _msg.format(desc)
            raise AttributeError(msg)

        # assert type given actually has a
        # binded constructor object
        if c is None:
            _msg = ("object type {!r} is missing "
                    "a constructor object")
            msg = _msg.format(typ)
            raise NoConstructorError(msg)

        # check required attributes
        if r is not None:
            if not isinstance(r, tuple):
                _msg = ("__required_keys__ must be of "
                        "tuple type; found {} (in constructor "
                        "{!r} ({}))")
                msg = _msg.format(type(r).__name__, c.__name__, c)
                raise TypeError(msg)
            for attr in c.__dict__.get("__required_keys__"):
                if attr not in desc:
                    _msg = ("required attriute {!r} missing "
                            "in description passed into "
                            "constructor {!r} ({}). desc is {}")
                    msg = _msg.format(attr, c.__name__, c, desc)
                    raise MissingRequiredKeysError(msg)

        # This allows for empty classes (such as `Compressor`)
        return c(desc) if bool(desc) else c()


class _PyHardwareObject:
    """Base hardware class.

    All hardware constructor objects should inherit from
    this class.
    """

    def __init_subclass__(cls):
        """Initialize hardware constructor objects.

        This exists to assert hardware constructors have
        the appropriate attributes, and to register
        the object and its type to the `HardwareObject`
        class. Supported custom attributes include
        `__type__` and `__required_keys__`.
        """

        # __type__ management
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

        # update public interface with constructor objects
        _objs = HardwareObject.__dict__.get("__objs__")
        # assert no duplicate __type__ values
        if _type in _objs:
            _msg = ("'__type__' attribute of constructor {!r} ({}) "
                    "has name {!r}, which was already defined "
                    "in constructor {!r} ({})")
            msg = _msg.format(cls.__name__, cls, _type,
                              _objs.get(_type).__name__,
                              _objs.get(_type))
            raise DuplicateTypeError(msg)

        print(f"adding type {_type!r} with object {cls.__name__!r} ({cls})")
        _objs.update({_type: cls})


class CANTalonSRX(_PyHardwareObject, ctre.WPI_TalonSRX):
    """
    Create a WPI_TalonSRX object.

    :param desc: Object description
    """

    __type__ = "CANTalonSRX"
    __required_keys__ = ('channel',)
    
    def __init__(self, desc):

        # Setup conditional variables
        self.has_pid = False

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
            self.has_pid = True
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

        if self.has_pid:
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
        self.has_pid = False

        # Define constructor variables
        channel = desc["channel"]

        # Initialize parent class
        ctre.WPI_TalonFX.__init__(self, channel)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            self.is_follower = True
            ctre.WPI_TalonFX.set(self,
                mode=ctre.TalonFXControlMode.Follower,
                value=desc["masterChannel"]
            )
        # Instantiate other pieces of the motor
        if "pid" in desc:
            self.has_pid = True
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

        if self.has_pid:
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
        self.coasting = False
        self.has_pid = False

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
            self.has_pid = True
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

        # XXX Why are we defining this? It's never used.
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

        if self.coasting:
            return
        self.coasting = True
        self.__set_control_type("kDutyCycle")
        self.PIDController.setReference(
            0, self.control_type, self.feedbackDevice)

    def __stop_coast(self):
        """
        Restores the previous control type and
        stops the motor from coasting.
        """

        if self.coasting:
            self.control_type = self.init_control_type
        self.coasting = False

    def set(self, speed, coast=True):
        """
        Set the speed for a SparkMax motor.
        """

        if self.has_pid:
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


class Breaksensors(_PyHardwareObject, wpilib.DigitalInput):
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
