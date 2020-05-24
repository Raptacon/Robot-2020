# -*- coding: utf-8 -*-

import rev
import ctre


def createMotor(motorDescp, motors={}):
    '''This is where all motors are set up.
    Motors include CAN Talons, CAN Talon Followers, CAN Talon FX, CAN Talon FX Followers, and SparkMax and its follower.
    Not all are functional, it's up to you to find out. Good luck!'''
    if motorDescp['type'] == 'CANTalonSRX':
        # If we want to use the built in encoder set it here
        if 'pid' in motorDescp and motorDescp['pid'] is not None:
            motor = WPI_TalonSRXFeedback(motorDescp)
            motor.setupPid()
        else:
            motor = ctre.WPI_TalonSRX(motorDescp['channel'])
        setTalonSRXCurrentLimits(motor, motorDescp)
        motors[str(motorDescp['channel'])] = motor

    elif motorDescp['type'] == 'CANTalonSRXFollower':
        '''This is where we set up Talon SRXs over CAN'''
        motor = ctre.WPI_TalonSRX(motorDescp['channel'])
        motor.set(mode=ctre.ControlMode.Follower, value=motorDescp['masterChannel'])
        setTalonSRXCurrentLimits(motor, motorDescp)
        motors[str(motorDescp['channel'])] = motor

    elif motorDescp['type'] == 'CANTalonFX':
        '''This is where CANTalon FXs are set up'''
        if 'pid' in motorDescp and motorDescp['pid'] is not None:
            motor = WPI_TalonFXFeedback(motorDescp)
            motor.setupPid()
        else:
            motor = ctre.WPI_TalonFX(motorDescp['channel'])
        setTalonFXCurrentLimits(motor, motorDescp)

    elif motorDescp['type'] == 'CANTalonFXFollower':
        '''This is where CANTalon FX Followers are set up'''
        motor = ctre.WPI_TalonFX(motorDescp['channel'])
        motor.set(mode=ctre.TalonFXControlMode.Follower, value=motorDescp['masterChannel'])
        motors[str(motorDescp['channel'])] = motor
        setTalonFXCurrentLimits(motor, motorDescp)

    elif motorDescp['type'] == 'SparkMax':
        '''This is where SparkMax motor controllers are set up'''
        motorDescp['motorType'] = getattr(rev.MotorType, motorDescp['motorType'])

        if 'pid' in motorDescp and motorDescp['pid'] is not None:
            motor = SparkMaxFeedback(motorDescp, motors)
            motor.setupPid()
        else:
            motor = rev.CANSparkMax(motorDescp['channel'], motorDescp['motorType'])

        motors[str(motorDescp['channel'])] = motor
        setREVCurrentLimits(motor, motorDescp)

    elif motorDescp['type'] == 'SparkMaxFollower':
        '''This is where SparkMax followers are set up
        For masterChannel, use a motor object. MASTER MUST BE A "CANSparkMax" because blame rev'''
        motorDescp['motorType'] = getattr(rev.MotorType, motorDescp['motorType'])
        motor = SparkMaxFeedback(motorDescp, motors)
        motor.follow(motors.get(str(motorDescp['masterChannel'])), motorDescp['inverted'])
        setREVCurrentLimits(motor, motorDescp)

    else:
        raise ValueError(f"Unknown Motor: {motorDescp['type']}")

    if 'inverted' in motorDescp:
        motor.setInverted(motorDescp['inverted'])

    return motor


def setTalonFXCurrentLimits(motor, motorDescp):
    """
    Sets current limits based off of "currentLimits"
    in your motor and config of choice. Must be a Talon FX motor controller
    In currentLimits, you need currentLimit, triggerThresholdCurrent, and triggerThresholdTime.
    """

    if 'currentLimits' in motorDescp:
        currentLimits = motorDescp['currentLimits']
        currentLimit = currentLimits['currentLimit']
        triggerThresholdCurrent = currentLimits['triggerThresholdCurrent']
        triggerThresholdTime = currentLimits['triggerThresholdTime']
        statorCurrentConfig = ctre.StatorCurrentLimitConfiguration(True, currentLimit, triggerThresholdCurrent, triggerThresholdTime)
        supplyCurrentConfig = ctre.SupplyCurrentLimitConfiguration(True, currentLimit, triggerThresholdCurrent, triggerThresholdTime)
        motor.configStatorCurrentLimit(statorCurrentConfig)
        motor.configSupplyCurrentLimit(supplyCurrentConfig)


def setTalonSRXCurrentLimits(motor, motorDescp):
    """
    Sets current limits based off of "currentLimits"
    in your motor and config of choice. Must be a Talon SRX motor controller
    In currentLimits, you need absMax, absMaxTimeMs, maxNominal.
    """

    if 'currentLimits' in motorDescp:
        currentLimits = motorDescp['currentLimits']
        absMax = currentLimits['absMax']
        absMaxTimeMs = currentLimits['absMaxTimeMs']
        nominalMaxCurrent = currentLimits['maxNominal']
        motor.configPeakCurrentLimit(absMax, 10)
        motor.configPeakCurrentDuration(absMaxTimeMs, 10)
        motor.configContinuousCurrentLimit(nominalMaxCurrent, 10)
        motor.enableCurrentLimit(True)


def setREVCurrentLimits(motor, motorDescp):
    """
    Sets current limits based off of "currentLimits"
    in your motor and config of choice. Must be a REV motor controller
    In currentLimits, you need freeLimit, stallLimit, stallLimitRPM and secondaryLimit
    """

    if 'currentLimits' in motorDescp:
        currentLimits = motorDescp['currentLimits']
        freeLimit = currentLimits['freeLimit']
        stallLimit = currentLimits['stallLimit']
        limitRPM = currentLimits['stallLimitRPM']
        secondaryLimit = currentLimits['secondaryLimit']
        motor.setSecondaryCurrentLimit(secondaryLimit)
        motor.setSmartCurrentLimit(stallLimit, freeLimit, limitRPM)


class WPI_TalonSRXFeedback(ctre.WPI_TalonSRX):  # ctre.wpi_talonsrx.WPI_TalonSRX
    """
    Class used to setup TalonSRX motors if there are PID setting for it
    """

    def __init__(self, motorDescription):
        ctre.WPI_TalonSRX.__init__(self, motorDescription['channel'])
        self.motorDescription = motorDescription
        self.pid = None

    def setupPid(self, motorDescription=None):
        '''Sets up PID based on dictionary motorDescription['pid'].
        This dictionary must contain controlType, feedbackDevice, sensorPhase, kPreScale, and P, I, D and F.'''
        if not motorDescription:
            motorDescription = self.motorDescription
        if 'pid' not in self.motorDescription:
            print("Motor channel %d has no PID" % (self.motorDescription['channel']))
            return
        self.pid = self.motorDescription['pid']

        # Takes a str and converts it to a ctre enum
        self.controlType = self.pid['controlType']
        if self.controlType == "Position":
            self.controlType = ctre.ControlMode.Position
        elif self.controlType == "Velocity":
            self.controlType = ctre.ControlMode.Velocity

        self.configSelectedFeedbackSensor(ctre.FeedbackDevice(self.pid['feedbackDevice']), 0, 10)
        self.setSensorPhase(self.pid['sensorPhase'])
        self.ControlType = self.pid['controlType']
        self.kPreScale = self.pid['kPreScale']

        # Set the peak, nominal outputs, and deadband
        self.configNominalOutputForward(0, 10)
        self.configNominalOutputReverse(0, 10)
        self.configPeakOutputForward(1, 10)
        self.configPeakOutputReverse(-1, 10)

        self.configVelocityMeasurementPeriod(ctre.VelocityMeasPeriod(1), 10)

        # Set closed loop gains in slot
        self.config_kF(0, self.pid['kF'], 10)
        self.config_kP(0, self.pid['kP'], 10)
        self.config_kI(0, self.pid['kI'], 10)
        self.config_kD(0, self.pid['kD'], 10)

    def set(self, speed):
        if self.pid is not None:
            return ctre.WPI_TalonSRX.set(self, self.controlType, speed * self.kPreScale)
        else:
            return self.set(speed)


class WPI_TalonFXFeedback(ctre.WPI_TalonFX):

    def __init__(self, motorDescription):
        '''Sets up the basic Talon FX with channel of motorDescription['channel']. Doesn't set up pid.'''
        ctre.WPI_TalonFX.__init__(self, motorDescription['channel'])
        self.motorDescription = motorDescription
        self.pid = None
        if self.motorDescription['type'] == "CANTalonFXFollower":
            self.controlType = ctre.TalonFXControlMode.Follower
        else:
            self.controlType = ctre.TalonFXControlMode.PercentOutput

    def setupPid(self, motorDescription=None):
        '''Sets up pid based on the dictionary motorDescription['pid']
        (Must contain channel, P, I, D, F, control type, sensorPhase (boolean), kPreScale, feedbackDevice)'''
        if not motorDescription:
            motorDescription = self.motorDescription
        if 'pid' not in self.motorDescription:
            print("Motor channel %d has no PID" % (self.motorDescription['channel']))
            return
        self.pid = self.motorDescription['pid']

        # Takes a str and converts it to a ctre enum for controltype.
        self.controlType = self.pid['controlType']
        if self.controlType == "Position":
            self.controlType = ctre.TalonFXControlMode.Position
        elif self.controlType == "Velocity":
            self.controlType = ctre.TalonFXControlMode.Velocity
        else:
            print("Unrecognized control type:", self.ControlType)

        self.configSelectedFeedbackSensor(ctre.FeedbackDevice(self.pid['feedbackDevice']), 0, 10)
        self.setSensorPhase(self.pid['sensorPhase'])
        self.kPreScale = self.pid['kPreScale']

        # Set the peak, nominal outputs, and deadband
        self.configNominalOutputForward(0, 10)
        self.configNominalOutputReverse(0, 10)
        self.configPeakOutputForward(1, 10)
        self.configPeakOutputReverse(-1, 10)
        self.configVelocityMeasurementPeriod(ctre.VelocityMeasPeriod(1), 10)
        # Set closed loop gains in slot
        self.config_kF(0, self.pid['kF'], 10)
        self.config_kP(0, self.pid['kP'], 10)
        self.config_kI(0, self.pid['kI'], 10)
        self.config_kD(0, self.pid['kD'], 10)

    def set(self, speed):
        """
        Overrides the default set() to allow for controll using the pid loop
        """
        if self.pid is not None:
            return ctre.WPI_TalonFX.set(self, self.controlType, speed * self.kPreScale)
        else:
            return ctre.WPI_TalonFX.set(self, speed)


class SparkMaxFeedback(rev.CANSparkMax):
    """
    Class used to setup SparkMax motor if there are PID settings for it - MUST CALL setupPID
    if you don't want it to crash. Great design decision on my part.
    """
    def __init__(self, motorDescription, motors):
        self.motorDescription = motorDescription
        self.motorType = self.motorDescription['motorType']

        rev.CANSparkMax.__init__(self, self.motorDescription['channel'], self.motorType)
        self.setInverted(self.motorDescription['inverted'])
        self.motors = motors
        self.coasting = False

    def setupPid(self):
        '''Sets up the PIDF values and a pidcontroller to use to control the motor using pid.'''
        if 'pid' not in self.motorDescription:
            print("Motor channel %f has no PID", (self.motorDescription['channel']))
            return
        self.pid = self.motorDescription['pid']
        pid = self.pid
        self.ControlType = pid['controlType']

        # Turns strings from pid dictionary in config into enums from rev library for control type
        if self.ControlType == "Position":
            self.ControlType = rev.ControlType.kPosition
        elif self.ControlType == "Velocity":
            self.ControlType = rev.ControlType.kVelocity
        else:
            print("Unrecognized control type:", self.ControlType)

        # If coastOnZero is true, when set() is called with a speed of 0, we will use DutyCycle
        # and let the motor spin down by itself (demonstrated in coast and stopcoast methods and within set()).
        if 'coastOnZero' in self.pid and self.pid['coastOnZero']:
            self.coastOnZero = True
        else:
            self.coastOnZero = False

        self.prevControlType = self.ControlType

        self.encoder = self.getEncoder()
        self.kPreScale = pid['kPreScale']  # Multiplier for the speed - lets you stay withing -1 to 1 for input but different outputs to pidController
        self.PIDController = self.getPIDController()  # Creates pid controller

        # Sets PID(F) values
        self.PIDController.setP(pid['kP'], pid['feedbackDevice'])  # pid['feedbackDevice'] is a slot for PID(F) configs. They range from 0-3.
        self.PIDController.setI(pid['kI'], pid['feedbackDevice'])
        self.PIDController.setD(pid['kD'], pid['feedbackDevice'])
        self.PIDController.setFF(pid['kF'], pid['feedbackDevice'])

        # Generally just a way to overwrite previous settings on any motor controller - We don't brake often.
        if 'IdleBrake' in self.motorDescription.keys() and self.motorDescription['IdleBrake']:
            self.setIdleMode(rev.IdleMode.kBrake)
        else:
            self.setIdleMode(rev.IdleMode.kCoast)

        # Configures output range - that's what Spark Maxes accept
        self.PIDController.setOutputRange(-1, 1, pid['feedbackDevice'])
        self.PIDController.setReference(0, self.ControlType, pid['feedbackDevice'])

    def setControlType(self, type: str):
        """
        Takes str type as argument, currently accepts Position, Velocity and Duty Cycle.
        More can be added as necessary, following previous syntax in this method.
        """

        if type == "Position":
            self.ControlType = rev.ControlType.kPosition
        elif type == "Velocity":
            self.ControlType = rev.ControlType.kVelocity
        elif type == "Duty Cycle":
            self.ControlType = rev.ControlType.kDutyCycle
        else:
            print("Unrecognized control type:", self.ControlType)

    def coast(self):
        """
        Stores the current control type, moves to Duty Cycle, sets to 0.
        """

        if self.coasting:
            return
        self.coasting = True
        self.prevControlType = self.ControlType
        self.setControlType("Duty Cycle")
        self.PIDController.setReference(0, self.ControlType, self.pid['feedbackDevice'])

    def stopCoast(self):
        """
        Restores previous control type. Whatever it was.
        """

        if self.coasting:
            self.ControlType = self.prevControlType
        self.coasting = False

    def set(self, speed):
        """
        Overrides the default set() to allow for control using the pid loop
        """

        if self.coastOnZero and speed == 0:
            self.coast()
        else:
            self.stopCoast()
        return self.PIDController.setReference(speed * self.pid['kPreScale'], self.ControlType, self.pid['feedbackDevice'])
