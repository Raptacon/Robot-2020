from magicbot import StateMachine, state, timed_state, feedback
from components.breakSensors import BreakSensors, Sensors, State
from components.hopper import Hopper
from wpilib import XboxController


AUTONOMOUS_SHOOTER_SPEED = 4800
TELEOP_SHOOTER_SPEED = 5300
SPEED_TOLERANCE = 50

class Shooter(StateMachine):

    hopper: Hopper
    breaksensors: BreakSensors

    inputs_XboxControllers: dict
    motors_shooter: dict
    
    def on_enable(self):
        self.autonomous = False  # NOTE this is changed in robot.py
        self.mech = self.inputs_XboxControllers["mech"]
        self.shooter_motor = self.motors_shooter["shooterMotor"]

    def startShooter(self):
        if self.hopper.loader_motor.get() != 0 or self.shooter_motor.get() != 0:
            return
        self.next_state("prepareShooter")

    @feedback
    def isShooterUpToSpeed(self):
        """Determines if the shooter is up to speed, then rumbles controller and publishes to NetworkTables."""
        if self.autonomous:
            shootSpeed = AUTONOMOUS_SHOOTER_SPEED - SPEED_TOLERANCE
        elif not self.autonomous:
            shootSpeed = TELEOP_SHOOTER_SPEED - SPEED_TOLERANCE
        atSpeed = bool(self.shooter_motor.getEncoder().getVelocity() >= shootSpeed)
        rumble  = 0
        if atSpeed and not self.isAutonomous:
            rumble = .3
        self.mech.setRumble(self.mech.RumbleType.kLeftRumble, rumble)
        self.mech.setRumble(self.mech.RumbleType.kRightRumble, rumble)
        return atSpeed

    @state
    def prepareShooter(self):
        """

        """

        if self.breaksensors.get(Sensors.kShootingSensor, State.kTripped):
            self.hopper.loader_motor.set(-.4)  # FIXME Get variable from hopper.py
        else:
            self.hopper.loader_motor.set(0)
            if self.autonomous:
                self.shooter_motor.set(AUTONOMOUS_SHOOTER_SPEED)
            else:
                self.shooter_motor.set(TELEOP_SHOOTER_SPEED)
            if self.isShooterUpToSpeed():
                self.next_state("shootBalls")

    @state
    def shootBalls(self):
        if not self.autonomous:
            # switch loader control to operators
            # regardless of intake type selected
            self.hopper.next_state("runLoaderManually")
        else:


    @state(first=True)
    def idling(self):
        """
        First state. Shooter does nothing here. StateMachine
        returns here whenever the shooter is inactive.
        """

        pass

    def execute(self):
        """

        """

        if self.mech.getRawButtonPressed(XboxController.Button.kA):
            pass

        self.engage()
        super().execute()
