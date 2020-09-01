import rev
import ctre


class _Generator:
    pass

class _MotorGenerator(_Generator):

    class CurrentLimits:
        """
        Holds current limit setters.
        """

        @staticmethod
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
                args = (True, currentLimit, triggerThresholdCurrent, triggerThresholdTime)
                statorCurrentConfig = ctre.StatorCurrentLimitConfiguration(*args)
                supplyCurrentConfig = ctre.SupplyCurrentLimitConfiguration(*args)
                motor.configStatorCurrentLimit(statorCurrentConfig)
                motor.configSupplyCurrentLimit(supplyCurrentConfig)

        @staticmethod
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

        @staticmethod
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


    class WPI_TalonSRXFeedback(ctre.WPI_TalonSRX):
        """
        Setup PID
        """

        def __init__(self, motor_descp):
            super().__init__(self, motor_descp['channel'])
            self.setupPid(motor_descp)

        def setupPid(self, motor_descp):
            """
            Sets up PID based on dictionary motorDescription['pid'].
            This dictionary must contain controlType, feedbackDevice,
            sensorPhase, kPreScale, and P, I, D and F.
            """

            self.pid = motor_descp['pid']

            self.controlType = self.pid['controlType']
            if self.controlType == "Position":
                self.controlType = ctre.ControlMode.Position
            elif self.controlType == "Velocity":
                self.controlType = ctre.ControlMode.Velocity
            
            feedback_device = ctre.FeedbackDevice(self.pid['feedbackDevice'])
            self.configSelectedFeedbackSensor(feedback_device, 0, 10)
            self.setSensorPhase(self.pid['sensorPhase'])
            self.kPreScale = self.pid['kPreScale']

            self.configNominalOutputForward(0, 10)
            self.configNominalOutputReverse(0, 10)
            self.configPeakOutputForward(1, 10)
            self.configPeakOutputReverse(-1, 10)
            self.configVelocityMeasurementPeriod(ctre.VelocityMeasPeriod(1), 10)
            self.config_kF(0, self.pid['kF'], 10)
            self.config_kP(0, self.pid['kP'], 10)
            self.config_kI(0, self.pid['kI'], 10)
            self.config_kD(0, self.pid['kD'], 10)

        def set(self, speed):
            if self.pid != None:
                return ctre.WPI_TalonSRX.set(self, self.controlType, speed * self.kPreScale)
            else:
                return self.set(speed)


    class WPI_TalonFXFeedback(ctre.WPI_TalonFX):
        """
        Setup PID
        """

        def __init__(self, motor_descp):
            """
            Sets up the basic Talon FX with channel of
            motorDescription['channel']. Doesn't set up pid.
            """

            super().__init__(self, motor_descp['channel'])
            if self.motorDescription['type'] == "CANTalonFXFollower":
                self.controlType = ctre.TalonFXControlMode.Follower
            else:
                self.controlType = ctre.TalonFXControlMode.PercentOutput
            self.setupPid(motor_descp)

        def setupPid(self, motor_descp):
            '''Sets up pid based on the dictionary motorDescription['pid']
            (Must contain channel, P, I, D, F, control type, sensorPhase (boolean), kPreScale, feedbackDevice)'''

            self.pid = motor_descp['pid']
            
            self.controlType = self.pid['controlType']
            if self.controlType == "Position":
                self.controlType = ctre.TalonFXControlMode.Position
            elif self.controlType == "Velocity":
                self.controlType = ctre.TalonFXControlMode.Velocity
            else:
                print("Unrecognized control type: ",self.ControlType)

            feedback_device = ctre.FeedbackDevice(self.pid['feedbackDevice'])
            self.configSelectedFeedbackSensor(feedback_device, 0, 10)
            self.setSensorPhase(self.pid['sensorPhase'])
            self.kPreScale = self.pid['kPreScale']

            self.configNominalOutputForward(0, 10)
            self.configNominalOutputReverse(0, 10)
            self.configPeakOutputForward(1, 10)
            self.configPeakOutputReverse(-1, 10)
            self.configVelocityMeasurementPeriod(ctre.VelocityMeasPeriod(1), 10)
            self.config_kF(0, self.pid['kF'], 10)
            self.config_kP(0, self.pid['kP'], 10)
            self.config_kI(0, self.pid['kI'], 10)
            self.config_kD(0, self.pid['kD'], 10)

        def set(self, speed):
            """
            Overrides the default set() to allow for controll using the pid loop
            """
            if self.pid != None:
                return ctre.WPI_TalonFX.set(self, self.controlType, speed * self.kPreScale)
            else:
                return ctre.WPI_TalonFX.set(self, speed)


    class SparkMaxFeedback(rev.CANSparkMax):
        """
        Class used to setup SparkMax motor if there are PID settings for it.
        """

        def __init__(self, motor_descp):
            motorType = motor_descp['motorType']
            super().__init__(self, self.motorDescription['channel'], motorType)
            self.setInverted(motor_descp['inverted'])
            self.coasting = False

        def setupPid(self, motor_descp):
            """
            Sets up the PIDF values and a pidcontroller to use to control the motor using pid.
            """

            pid = motor_descp['pid']
            self.ControlType = pid['controlType']
            
            # Turns strings from pid dictionary in config into enums from rev library for control type
            if self.ControlType == "Position":
                self.ControlType = rev.ControlType.kPosition
            elif self.ControlType == "Velocity":
                self.ControlType = rev.ControlType.kVelocity
            else:
                print("Unrecognized control type: ",self.ControlType)

            #If coastOnZero is true, when set() is called with a speed of 0, we will use DutyCycle
            #And let the motor spin down by itself. (demonstrated in coast and stopcoast methods and within set())
            if 'coastOnZero' in self.pid and self.pid['coastOnZero'] == True:
                self.coastOnZero = True
            else:
                self.coastOnZero = False

            self.prevControlType = self.ControlType

            self.encoder = self.getEncoder()
            self.kPreScale = pid['kPreScale']  # Multiplier for the speed - lets you stay withing -1 to 1 for input but different outputs to pidController
            self.PIDController = self.getPIDController()  # Creates pid controller

            #Sets PID(F) values
            self.PIDController.setP(pid['kP'], pid['feedbackDevice'])
            self.PIDController.setI(pid['kI'], pid['feedbackDevice'])
            self.PIDController.setD(pid['kD'], pid['feedbackDevice'])
            self.PIDController.setFF(pid['kF'], pid['feedbackDevice'])
            
            # Generally just a way to overwrite previous settings on
            # any motor controller - We don't brake often.
            if 'IdleBrake' in self.motorDescription.keys() \
                and self.motorDescription['IdleBrake'] == True:
                self.setIdleMode(rev.IdleMode.kBrake)
            else:
                self.setIdleMode(rev.IdleMode.kCoast)
            
            #Configures output range - that's what Spark Maxes accept
            self.PIDController.setOutputRange(-1, 1, pid['feedbackDevice'])
            self.PIDController.setReference(0 , self.ControlType, pid['feedbackDevice'])

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
                print(f"Unrecognized control type: {self.ControlType}")

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
            return self.PIDController.setReference(
                                        speed*self.pid['kPreScale'],
                                        self.ControlType,
                                        self.pid['feedbackDevice'])

        # if motor_type == 'CANTalonSRX':
        #     if 'pid' in motor_descp and motor_descp['pid'] is not None:
        #         motor = WPI_TalonSRXFeedback(motor_descp)
        #     else:
        #         motor = ctre.WPI_TalonSRX(motor_descp['channel'])
        #     CurrentLimits.setTalonSRXCurrentLimits(motor, motor_descp)
        #     motors[str(motor_descp['channel'])] = motor

        # elif motor_type == 'CANTalonSRXFollower':
        #     motor = ctre.WPI_TalonSRX(motor_descp['channel'])
        #     motor.set(mode=ctre.ControlMode.Follower, value=motor_descp['masterChannel'])
        #     CurrentLimits.setTalonSRXCurrentLimits(motor, motor_descp)
        #     motors[str(motor_descp['channel'])] = motor

        # elif motor_type == 'CANTalonFX':
        #     if 'pid' in motor_descp and motor_descp['pid'] is not None:
        #         motor = WPI_TalonFXFeedback(motor_descp)
        #     else:
        #         motor = ctre.WPI_TalonFX(motor_descp['channel'])
        #     CurrentLimits.setTalonFXCurrentLimits(motor, motor_descp)

        # elif motor_type == 'CANTalonFXFollower':
        #     motor = ctre.WPI_TalonFX(motor_descp['channel'])
        #     motor.set(mode=ctre.TalonFXControlMode.Follower, value=motor_descp['masterChannel'])
        #     motors[str(motor_descp['channel'])] = motor
        #     CurrentLimits.setTalonFXCurrentLimits(motor, motor_descp)

        # elif motor_type == 'SparkMax':
        #     motor_descp['motorType'] = getattr(rev.MotorType, motor_descp['motorType'])

        #     if 'pid' in motor_descp and motor_descp['pid'] is not None:
        #         motor = SparkMaxFeedback(motor_descp)
        #         motor.setupPid(motor_descp)
        #     else:
        #         motor = rev.CANSparkMax(motor_descp['channel'],
        #                                 motor_descp['motorType'])

        #     CurrentLimits.setREVCurrentLimits(motor, motor_descp)
        #     motors[str(motor_descp['channel'])] = motor

        # elif motor_type == 'SparkMaxFollower':
        #     motor_descp['motorType'] = getattr(rev.MotorType, motor_descp['motorType'])
        #     motor = SparkMaxFeedback(motor_descp)
        #     motor.follow(motors.get(str(motor_descp['masterChannel'])), motor_descp['inverted'])
        #     CurrentLimits.setREVCurrentLimits(motor, motor_descp)


