from robotMap import XboxMap
from components.shooterMotors import ShooterMotorCreation, Direction
from magicbot import StateMachine, state, timed_state, tunable
import logging
from enum import IntEnum

class Sensors(IntEnum):
    """Enum for sensors."""
    kLoadingSensor = 0
    kShootingSensor = 4

class ShooterLogic(StateMachine):
    """StateMachine-based shooter. Has both manual and automatic modes."""
    compatString = ["doof"]

    # Component/module related things
    digitalInput_breaksensors: dict
    logger: logging
    shooterMotors: ShooterMotorCreation
    xboxMap: XboxMap

    # Tunables
    loaderMotorSpeed = tunable(.4)
    intakeMotorMinSpeed = tunable(.5)
    intakeMotorMaxSpeed = tunable(.7)
    targetShootingSpeed = tunable(5300)

    # Other variables
    shooterStoppingDelay = 2

    def on_enable(self):
        """Called when bot is enabled."""
        self.SensorArray = []
        self.isAutomatic = False
        self.isAutonomous = False

        # Creates sensors:
        for x in range(1, 6):
            self.SensorArray.append(self.digitalInput_breaksensors["sensor" + str(x)])
            # NOTE: Sensor keys are different than dio value:
            # dio(1) >>> SensorArray[0]
            # dio(2) >>> SensorArray[1]
            # dio(3) >>> SensorArray[2]
            # dio(4) >>> SensorArray[3]
            # dio(5) >>> SensorArray[4]

        # self.logger.setLevel(logging.DEBUG)

    def setAutoLoading(self):
        """Runs sensor-based loading."""
        self.isAutomatic = True
        self.next_state('checkForBall')

    def setManualLoading(self):
        """Runs trigger-based loading."""
        self.isAutomatic = False
        self.next_state('runLoaderManually')

    def shootBalls(self):
        """Executes smart shooter."""
        if self.shooterMotors.isLoaderRunning() or self.shooterMotors.isShooterRunning():
            return False
        else:
            self.next_state('initShooting')
            return True

    # NOTE: This is a temporary func, we should make this integraded with the normal shooter
    def shootAutonomous(self):
        self.isAutonomous = True

    def runIntake(self):
        """Universal function for running the intake. Used in both manual and automatic."""
        if self.xboxMap.getMechRightTrig() > 0 and self.xboxMap.getMechLeftTrig() == 0:
            self.shooterMotors.runIntake((self.xboxMap.getMechRightTrig()*(self.intakeMotorMaxSpeed-self.intakeMotorMinSpeed))+self.intakeMotorMinSpeed, Direction.kForwards)
            self.logger.debug("right trig intake", self.xboxMap.getMechRightTrig())

        elif self.xboxMap.getMechLeftTrig() > 0 and self.xboxMap.getMechRightTrig() == 0:
            self.shooterMotors.runIntake((self.xboxMap.getMechRightTrig()*(self.intakeMotorMaxSpeed-self.intakeMotorMinSpeed))+self.intakeMotorMinSpeed, Direction.kBackwards)
            self.logger.debug("left trig intake", self.xboxMap.getMechLeftTrig())

        else:
            self.shooterMotors.stopIntake()

    # Beginning of manual
    @state(first = True)
    def runLoaderManually(self):
        """Trigger-based manual loader."""
        self.shooterMotors.stopShooter()
        if self.xboxMap.getMechRightTrig() > 0 and self.xboxMap.getMechLeftTrig() == 0:
            self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)
            self.logger.debug("right trig manual", self.xboxMap.getMechRightTrig())

        elif self.xboxMap.getMechLeftTrig() > 0 and self.xboxMap.getMechRightTrig() == 0:
            self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kBackwards)
            self.logger.debug("left trig manual", self.xboxMap.getMechLeftTrig())

        else:
            self.shooterMotors.stopLoader()

    @state
    def checkForBall(self):
        """Checks for ball to enter the loader, runs the loader if entry sensor is broken."""
        self.shooterMotors.stopLoader()
        if not self.SensorArray[Sensors.kLoadingSensor].get():
            self.next_state('loadBall')

    @state
    def loadBall(self):
        """Loads ball if ball has entered."""
        self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)
        self.next_state('waitForBallIntake')

    @state
    def waitForBallIntake(self):
        """Checks for intake to be completed."""
        if self.SensorArray[Sensors.kLoadingSensor].get():
            self.next_state('stopBall')

    @timed_state(duration = .2, next_state = 'checkForBall')
    def stopBall(self):
        """Stops ball after a short delay."""
        pass

    @state
    def initShooting(self):
        """Smart shooter initialization (reversing if necessary)."""
        if not self.SensorArray[Sensors.kShootingSensor].get():
            self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kBackwards)

        elif self.SensorArray[Sensors.kShootingSensor].get():
            self.shooterMotors.stopLoader()
            if self.isAutonomous:
                self.next_state('runShooterAutonomous')
            elif not self.isAutonomous:
                self.next_state('runShooter')

    @state
    def runShooter(self, state_tm):
        """Runs shooter to a certain speed or until a set time."""
        self.shooterMotors.runShooter(1)
        if self.shooterMotors.shooterMotor.getEncoder().getVelocity() >= self.targetShootingSpeed or state_tm > 3:
            if self.xboxMap.getMechRightTrig() > 0 and self.xboxMap.getMechLeftTrig() == 0:
                self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)
                self.logger.debug("right trig manual", self.xboxMap.getMechRightTrig())

            elif self.xboxMap.getMechLeftTrig() > 0 and self.xboxMap.getMechRightTrig() == 0:
                self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kBackwards)
                self.logger.debug("left trig manual", self.xboxMap.getMechLeftTrig())

            else:
                self.shooterMotors.stopLoader()

    # @timed_state(duration = shooterStoppingDelay, next_state = 'stopShooter')
    # def shoot(self):
    #     """Runs loader for a set time after shooter is at speed."""
    #     self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)

    @state
    def runShooterAutonomous(self, state_tm):
        self.shooterMotors.runShooter(1)
        if self.shooterMotors.shooterMotor.getEncoder().getVelocity() >= self.targetShootingSpeed or state_tm > 3:
            self.next_state('runLoaderAutonomous')

    @timed_state(duration = shooterStoppingDelay, next_state = 'stopShooter')
    def runLoaderAutonomous(self):
        self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)

    @state
    def stopShooter(self):
        """Halts all shooter-related tasks and resets to 'checkForBall' state."""
        self.shooterMotors.stopLoader()
        self.shooterMotors.stopShooter()
        if self.isAutonomous = True:
            self.next_state('runLoaderManually')
            self.isAutonomous = False

    def nextAction(self):
        """Determines next loading type."""
        if self.isAutomatic:
            self.next_state_now('checkForBall')
        else:
            self.next_state_now('runLoaderManually')


    def execute(self):
        """Constantly runs state machine. Necessary for function."""
        self.engage()
        self.runIntake()
        super().execute()
