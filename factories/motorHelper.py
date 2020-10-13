"""Create Python objects for hardware components on the robot.

To add a new hardware object, create a class that inherits from
a base object from an API (such as CTRE, REV, WPILib, navX, etc.)
and manipulate it appropriately (add custom methods, instantiate
it with `super().__init__(), etc.). Once ready to be used, add it
to the `HardwareComponents` list near the bottom of this module,
giving an appropriate key to search for in a configuration file
and the Python object that should be used to create the component.
"""

import ctre
import rev
import wpilib
import navx

import time
import threading

from utils.filehandler import FileHandler


# TODO assert no empty/null keys in config (simplify if-statements)
# XXX why do we return on `set()` methods?
class WPI_TalonSRXMotor(ctre.WPI_TalonSRX):
    """
    Create a TalonSRX motor.

    NOTE: This object overrides the default `set()` method
    built into CTRE objects. To call the default set, use
    `super().set()`.
    """

    def __init__(self, desc):

        # Setup conditional variables
        self.has_pid = False

        # Define constructor variables
        channel = desc["channel"]

        # Initialize parent class
        super().__init__(channel)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            super().set(
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
        Setup PID for a TalonSRX motor
        """

        control_type = pid_desc["controlType"]
        self.control_type = getattr(ctre.ControlMode, control_type)

        self.configSelectedFeedbackSensor(
            ctre.FeedbackDevice(
                pid_desc['feedbackDevice']), 0, 10)
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
        Setup current limits for a TalonSRX motor.
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
        Sets the motor to a value appropriately.
        """

        return super().set(self, self.control_type,
                           speed * self.kPreScale) \
            if self.has_pid else self.set(speed)


class WPI_TalonFXMotor(ctre.WPI_TalonFX):
    """
    Create a TalonFX motor.

    NOTE: This object overrides the default `set()` method
    built into CTRE objects. To call the default set, use
    `super().set()`.
    """

    def __init__(self, desc):

        # Setup conditional variables
        self.has_pid = False

        # Define constructor variables
        channel = desc["channel"]

        # Initialize parent class
        super().__init__(channel)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            self.is_follower = True
            super().set(
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

        self.configSelectedFeedbackSensor(
            ctre.FeedbackDevice(
                pid_desc['feedbackDevice']), 0, 10)
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
        Setup current limits for a TalonFX motor.
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
        Sets the motor to a value appropriately.
        """

        return super().set(self, self.controlType,
                           speed * self.kPreScale) \
            if self.has_pid else super().set(self, speed)


class REV_SparkMaxMotor(rev.CANSparkMax):
    """
    Create a SparkMax motor.

    NOTE: This object overrides the default `set()` method
    built into REV objects. To call the default set, use
    `super().set()`.
    """

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
        motor_type = getattr(rev.ControlType, desc["motorType"])

        # Initialize parent class
        super().__init__(channel, motor_type)

        # Check motor parameters and setup motor accordingly
        if "follower" in desc:
            # For consistancy with the CTRE motors,
            # use `super()` here
            super().follow(
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
        Setup current limits for a SparkMax motor.
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
        self.__set_control_type("Duty Cycle")
        self.PIDController.setReference(
            0, self.ControlType, self.feedbackDevice)

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
        Sets the motor to a value appropriately.
        """

        if self.has_pid:
            self.__coast() if coast and speed == 0 else self.__stop_coast()
            args = [speed * self.kPreScale,
                    self.control_type,
                    self.feedbackDevice]
            return self.PIDController.setReference(*args)
        return super().set(speed)


class WPI_Compressor(wpilib.Compressor):
    """
    Creates a compressor object.
    """


class WPI_Solenoid(wpilib.Solenoid):
    """
    Creates a solenoid object.
    """

    def __init__(self, desc):
        pcm = 0
        if "pcm" in desc:
            pcm = desc["pcm"]
        super().__init__(pcm, desc["channel"])


class WPI_DoubleSolenoid(wpilib.DoubleSolenoid):
    """
    Creates a double solenoid object.
    """

    def __init__(self, desc):
        pcm = 0
        if "pcm" in desc:
            pcm = desc["pcm"]
        super().__init__(pcm,
                         desc["channel"]["forward"],
                         desc["channel"]["reverse"])
        if "default" in desc:
            default_pos = {
                "kOff": 0, "kForward": 1, "kReverse": 2
            }[desc["default"]]
            self.set(wpilib.DoubleSolenoid.Value(default_pos))


class NAVX_navX(navx.AHRS):
    """
    Creates a navX object.
    """

    def __init__(self, desc):
        method = desc["method"]
        if method == "spi":
            super().create_spi()
        elif method == "i2c":
            super().create_i2c()


class WPI_DigitalInput(wpilib.DigitalInput):
    """
    Creates a digital input object
    """

    def __init__(self, desc):
        channel = desc["channel"]
        super().__init__(channel)

    def __str__(self):
        return f"Controller object <{self}> on channel {self.getChannel}"


class WPI_XboxController(wpilib.XboxController):
    """
    Creates an Xbox controller object
    """

    def __init__(self, desc):

        super().__init__(desc["channel"])
        self.controller = self

        def update():
            delay = 0.020
            while True:
                time.sleep(delay)
                self.leftY = self.getRawAxis(
                    self.Axis.kLeftY)
                self.leftX = self.getRawAxis(
                    self.Axis.kLeftX)
                self.rightY = self.getRawAxis(
                    self.Axis.kRightY)
                self.rightX = self.getRawAxis(
                    self.Axis.kRightX)
                self.leftTrigger = self.getRawAxis(
                    self.Axis.kLeftTrigger)
                self.rightTrigger = self.getRawAxis(
                    self.Axis.kRightTrigger)
                self.pov = self.getPOV()

        updater = threading.Thread(target=update)
        updater.start()

    # TODO add __str__ methods like this to other classes
    def __str__(self):
        return f"Controller object <{self}> on channel {self.getPort}"


class _Mapping:
    """
    Simple object to map items, with additional
    `add` and `get` functions for readability.
    """

    def add(self, name, item):
        self.__dict__[name] = item

    def get(self, name):
        return self.__dict__[name]

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, name, val):
        self.__dict__[name] = val


class _HardwareComponents(_Mapping):
    """
    Container for mapping hardware components
    to their appropriate constructor object.
    """


# Construct _HardwareComponents object
HardwareComponents = _HardwareComponents()

# Register components
HardwareComponents.add("CANTalonSRX", WPI_TalonSRXMotor)
HardwareComponents.add("CANTalonFX", WPI_TalonFXMotor)
HardwareComponents.add("SparkMax", REV_SparkMaxMotor)
HardwareComponents.add("compressor", WPI_Compressor)
HardwareComponents.add("solenoid", WPI_Solenoid)
HardwareComponents.add("doubleSolenoid", WPI_DoubleSolenoid)
HardwareComponents.add("navx", NAVX_navX)
HardwareComponents.add("breaksensor", WPI_DigitalInput)
HardwareComponents.add("XboxController", WPI_XboxController)


# class GenerateHardwareObjects(FileHandler):
#     """
#     Generate hardware objects from json data.
#     """

#     def __init__(self, robot, json_file=None):
#         loaded_file = self.load(json_file) \
#             if json_file.__class__ == str else json_file
#         self._generate_objects(robot, loaded_file)

#     def _new_hardware_object(self, desc=None, mapping=None):
#         """
#         Create a new hardware object.
#         This method is a factory, capable of creating Python
#         hardware objects from a hardware mapping.

#         :param desc: Valid description of the hardware object, usually
#         found in a JSON configuration file.

#         :param mapping: Valid mapping object that inherits from the
#         `_Mapping` class.
#         """

#         # Assert mapping is actually a formatted mapping
#         if "_Mapper" not in mapping.__bases__ or mapping.__bases__ is None:
#             raise ValueError(
#                 f"invalid mapping: expected _Mapping, found {mapping.__bases__}"
#             )
#         obj_type = desc.pop("type")
#         constructor = mapping.get(obj_type)

#         # This allows for empty objects with default parent objects
#         # (i.e. WPI_Compressor)
#         return constructor() if not bool(desc) else constructor(desc)

#     def _generate_objects(self, robot, loaded_data):
#         for general_type, all_objects in loaded_data.items():
#             for subsystem_name, subsystem_items in all_objects.items():
#                 group_subsystem = "_".join([general_type, subsystem_name])
#                 for item_name, item_desc in subsystem_items.items():
#                     subsystem_items[item_name] = \
#                         self._new_hardware_object(
#                             desc=item_desc,
#                             mapping=HardwareComponents)
#                 setattr(robot, group_subsystem, subsystem_items)

loaded_data = FileHandler.load("new_doof.json")

class HardwareMeta(type):

    @classmethod
    def __prepare__(metacls, cls, bases):

        class _Map(dict):

            def __init__(self):
                super().__init__()

            def _add(self, name, item):
                self.__dict__[name] = item
            
            def __getattr__(self, attr):
                return self.__dict__[attr]

        return _Map()

    def __new__(metacls, cls, bases, namespace):
        for general_type, all_objects in loaded_data.items():
            g = super().__new__(metacls, general_type, (), {})
            for subsystem_name, subsystem_items in all_objects.items():
                s = super().__new__(metacls, subsystem_name, (), {})
                for item_name, item_desc in subsystem_items.items():
                    # TODO fix line length (PEP8)
                    s._add(item_name, metacls._new_hardware_object(item_desc, HardwareComponents))
                g._add(subsystem_name, s)
            namespace.update({general_type: g})

        return super().__new__(metacls, cls, bases, namespace)

    @staticmethod
    def _new_hardware_object(desc=None, mapping=None):
        """
        Create a new hardware object.
        This method is a factory, capable of creating Python
        hardware objects from a hardware mapping.

        :param desc: Valid description of the hardware object, usually
        found in a JSON configuration file.

        :param mapping: Valid mapping object that inherits from the
        `_Mapping` class.
        """

        # Assert mapping is actually a formatted mapping
        if "_Mapper" not in mapping.__bases__ or mapping.__bases__ is None:
            raise ValueError(
                f"invalid mapping: expected _Mapping, found {mapping.__bases__}"
            )
        obj_type = desc.pop("type")
        constructor = mapping.get(obj_type)

        # This allows for empty objects with default parent objects
        # (i.e. WPI_Compressor)
        return constructor() if not bool(desc) else constructor(desc)

class Hardware(metaclass=HardwareMeta):
    pass

# Hardware.motors.driveTrain.leftMotor
