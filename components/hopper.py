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

import pathlib


class Hopper(StateMachine):

    breaksensors: BreakSensors

    inputs_XboxControllers: dict
    motors_loader: dict

    automatic = True
    hopper_speed = tunable(.4)
    autonomous_loader_duration = tunable(3)

    def on_enable(self):
        self.mech = self.inputs_XboxControllers["mech"]
        self.hopper_motor = self.motors_loader["hopperMotor"]

    @state(first=True)
    def determineLoadingType(self):
        self.setHopper(0)
        if self.automatic:
            self.next_state("checkForBall")
        else:
            self.next_state("controlHopperManually")

    @state
    def controlHopperManually(self):
        if self.mech.getAxis(XboxController.Axis.kRightTrigger) > 0:
            self.setHopper(self.hopper_speed)
        elif self.mech.getAxis(XboxController.Axis.kLeftTrigger) > 0:
            self.setHopper(-self.hopper_speed)

    # START automatic loading logic
    @state
    def checkForBall(self):
        self.setHopper(0)
        if self.breaksensors.get(Sensors.kLoadingSensor, State.kTripped):
            self.next_state("loadBall")

    @state
    def loadBall(self):
        """Loads ball if ball has entered."""
        self.setHopper(self.hopper_speed)
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
    # END automatic loading logic

    def setHopper(self, speed):
        self.hopper_motor.set(speed)

    def execute(self):
        """

        """

        # Toggle loading types with XboxController.Button.kY
        if self.mech.getRawButtonPressed(XboxController.Button.kY):
            self.automatic = False
            self.next_state("determineLoadingType")

        if self.mech.getRawButtonPressed(XboxController.Button.kY) and not self.automatic:
            self.automatic = True
            self.next_state("determineLoadingType")

        # HACK to constantly run state machine
        self.engage()
        super().execute()

