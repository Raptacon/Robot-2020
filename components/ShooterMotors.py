
class ShooterMotorCreation:

    motorsList: dict

    def setup(self):
        self.intakeSpeed = 0
        self.loaderSpeed = 0
        self.shooterSpeed = 0
        self.intake = False
        self.loader = False
        self.shooter = False

        self.motors = self.motorsList

        self.loaderMotor = self.motors["loaderMotor"]
        self.intakeMotor = self.motors["intakeMotor"]
        self.shooterMotor = self.motors["shooterMotor"]

        print("shooter motors created")

    def runLoader(self, lSpeed):
        self.loaderSpeed = lSpeed
        self.loader = True

    def runIntake(self, iSpeed):
        self.intakeSpeed = iSpeed
        self.intake = True

    def runShooter(self, sSpeed):
        self.shooterSpeed = sSpeed
        self.shooter = True

    def stopIntake(self):
        self.intake = False

    def stopLoader(self):
        self.loader = False

    def stopShooter(self):
        self.shooter = False

    def isLoaderActive(self):
        return self.loader

    def execute(self):
        if self.intake:
            self.intakeMotor.set(self.intakeSpeed)
        elif self.intake == False:
            self.intakeMotor.set(0)

        if self.loader:
            self.loaderMotor.set(self.loaderSpeed)
        elif self.loader == False:
            self.loaderMotor.set(0)

        if self.shooter:
            self.shooterMotor.set(self.shooterSpeed)
        elif self.shooter == False:
            self.shooterMotor.set(0)
