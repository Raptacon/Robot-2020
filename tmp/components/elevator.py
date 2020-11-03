from magicbot import tunable

class Elevator:

    robot = ["doof"]

    motors_elevator: dict
    downSpeed = tunable(-.4)
    upSpeed = tunable(.4)

    def on_enable(self):
        self.speed = 0
        self.elevatorMotor = self.motors_elevator['elevatorMotor']
        print("Elevator Enabled")

    def setRaise(self):
        self.speed = self.upSpeed

    def setLower(self):
        self.speed = self.downSpeed

    def stop(self):
        self.speed = 0
    
    def execute(self):
        self.elevatorMotor.set(self.speed)
