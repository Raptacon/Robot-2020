from wpilib import XboxController


INTAKE_MOTOR_SPEED = 0.7


class Intake:

    inputs_XboxControllers: dict
    motors_intake: dict

    def on_enable(self):
        self.mech = self.inputs_XboxControllers["mech"]
        self.intake_motor = self.motors_intake["intakeMotor"]

    def runIntake(self):
        if self.mech.getAxis(XboxController.Axis.kRightTrigger) > 0:
            self.intake_motor.set(INTAKE_MOTOR_SPEED)
        elif self.mech.getAxis(XboxController.Axis.kLeftTrigger) > 0:
            self.intake_motor.set(-INTAKE_MOTOR_SPEED)

    def execute(self):
        self.runIntake()
