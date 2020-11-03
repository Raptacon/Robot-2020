from magicbot import (
    StateMachine,
    state,
    timed_state,
    tunable,
    feedback
)
from components.breakSensors import (
    BreakSensors,
    Sensors,
    State
)
from wpilib import XboxController


AUTOMATIC = True
LOADER_SPEED = .4


class Hopper(StateMachine):

    breaksensors: BreakSensors

    inputs_XboxControllers: dict
    motors_loader: dict

    def on_enable(self):
        self.mech = self.inputs_XboxControllers["mech"]
        self.loader_motor = self.motors_loader["loader"]
        self._loader_active = True

    @state
    def runLoaderManually(self):
        if self.mech.getAxis(XboxController.Axis.kRightTrigger) > 0:
            self.runLoader(LOADER_SPEED)
        elif self.mech.getAxis(XboxController.Axis.kLeftTrigger) > 0:
            self.runLoader(-LOADER_SPEED)

    @state
    def checkForBall(self):
        if self.breaksensors.get(Sensors.kLoadingSensor, State.kTripped):
            self.next_state("loadBall")

    @state
    def loadBall(self):
        """Loads ball if ball has entered."""
        self.runLoader(LOADER_SPEED)
        self.next_state('waitForBallIntake')

    @state
    def waitForBallIntake(self):
        """Checks for intake to be completed."""
        if self.breaksensors.get(Sensors.kLoadingSensor, State.kNotTripped):
            self.next_state('stopBall')

    @timed_state(duration=.16, next_state='checkForBall')
    def stopBall(self):
        """Stops ball after a short delay."""
        pass

    @state(first=True)
    def determineLoadingType(self):
        self.motors_loader.set(0)
        if AUTOMATIC:
            self.next_state("checkForBall")
        else:
            self.next_state("runLoaderManually")

    def runLoader(self, speed):
        self._loader_active = True

    def execute(self):
        """

        """

        # Toggle loading types with XboxController.Button.kY
        if self.mech.getRawButtonPressed(XboxController.Button.kY):
            AUTOMATIC = False
            self.next_state("determineLoadingType")

        if self.mech.getRawButtonPressed(XboxController.Button.kY) and not AUTOMATIC:
            AUTOMATIC = True
            self.next_state("determineLoadingType")

        if self._loader_active:
            self.loader_motor.set(LOADER_SPEED) 

        # HACK to constantly run state machine
        self.engage()
        super().execute()

