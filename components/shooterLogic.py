from robotMap import XboxMap
from components.shooterMotors import ShooterMotorCreation, Direction
from components.breakSensors import Sensors, State
from components.feederMap import FeederMap, Type
from magicbot import StateMachine, state, timed_state, tunable, feedback
from networktables import NetworkTables
import logging

class ShooterLogic(StateMachine):
    """StateMachine-based shooter. Has both manual and automatic modes."""
    compatString = ["doof"]

    # Component/module related things
    shooterMotors: ShooterMotorCreation
    feeder: FeederMap
    logger: logging
    sensors: Sensors
    xboxMap: XboxMap

    # Tunables
    loaderMotorSpeed = tunable(.3)
    targetShootingSpeed = tunable(5600)

    # Other variables
    isSetup = False
    shooterStoppingDelay = 3
    # FIXME: Need to figure out how to get valued from network tables
    # botMode = NetworkTables.getTable("SmartDashboard").getSubTable("NetworkTables").getSubTable("robot").getString("mode", "none")

    def on_enable(self):
        """Called when bot is enabled."""
        self.isAutonomous = False
        self.isSetup = True

        # self.logger.setLevel(logging.DEBUG)

    def autonomousEnabled(self):
        """Indicates the robot is in autonomous mode."""
        self.isAutonomous = True

    def autonomousDisabled(self):
        """Indicates the robot is not in autonomous mode."""
        self.isAutonomous = False

    def shootBalls(self):
        """Executes smart shooter."""
        if self.shooterMotors.isLoaderRunning() or self.shooterMotors.isShooterRunning():
            return False
        self.next_state('initShooting')
        return True

    def doneShooting(self):
        """Finishes shooting process and reverts back to appropriate mode."""
        self.next_state('finishShooting')

    @feedback
    def isShooterUpToSpeed(self):
        if not self.isSetup:
            return False
        atSpeed = bool(self.shooterMotors.shooterMotor.getEncoder().getVelocity() >= self.targetShootingSpeed)
        rumble  = 0
        if atSpeed:
            rumble = .3
        self.xboxMap.mech.setRumble(self.xboxMap.mech.RumbleType.kLeftRumble, rumble)
        self.xboxMap.mech.setRumble(self.xboxMap.mech.RumbleType.kRightRumble, rumble)
        return atSpeed

    # @feedback
    # def currentBotMode(self):


    @state
    def initShooting(self):
        """Smart shooter initialization (reversing if necessary)."""
        if self.sensors.shootingSensor(State.kTripped):
            self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kBackwards)

        else:
            self.shooterMotors.stopLoader()
            self.next_state('runShooter')

    @state
    def runShooter(self, tm):
        """
        Runs shooter to a certain speed, then lets drivers control loading if in teleop.
        If in autonomous, run shooter automatically.
        """
        self.shooterMotors.runShooter(1)
        if self.isShooterUpToSpeed() and not self.isAutonomous:
            self.feeder.run(Type.kLoader)

        elif self.isShooterUpToSpeed() and self.isAutonomous:
            self.next_state('autoShoot')

    @timed_state(duration = shooterStoppingDelay, next_state = 'finishShooting')
    def autonomousShoot(self):
        """Shoot balls when shooter is up to speed. Strictly for autonomous use."""
        self.shooterMotors.runLoader(self.loaderMotorSpeed, Direction.kForwards)

    @state
    def finishShooting(self):
        """Stops shooter-related motors and moves to idle state."""
        self.shooterMotors.stopLoader()
        self.shooterMotors.stopShooter()
        self.next_state('idling')

    @state(first = True)
    def idling(self):
        """First state. Does nothing here."""
        pass

    def execute(self):
        """Constantly runs state machine. Necessary for function."""
        self.engage()
        super().execute()
