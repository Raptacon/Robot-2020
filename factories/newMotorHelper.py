import rev, ctre


VALID_MOTOR_TYPES = [
    "CANTalonSRX",
    "CANTalonSRXFollower",
    "CANTalonFX",
    "CANTalonFXFollower",
    "SparkMax",
    "SparkMaxFollower"
]


class MotorFactory:

    def __init__(self, descp):
        self.createMotor(descp)
    
    def createMotor(self, motor_desp):
        pass