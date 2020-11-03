class Winch:

    inputs_XboxControllers: dict
    motors_winch: dict

    def on_enable(self):
        self.mech = self.inputs_XboxControllers["mech"]
        self.winch_motor = self.motors_winch["winchMotor"]

    def execute(self):
        if self.mech.getPOV() == 0:
            speed = 0
        else:
            speed = .5

        self.winch_motor.set(speed)
