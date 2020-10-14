from magicbot import AutonomousStateMachine, tunable, timed_state, state
from configs.components.driveTrain import DriveTrain
from configs.components.shooterLogic import ShooterLogic
from configs.components.shooterMotors import ShooterMotorCreation
from configs.components.pneumatics import Pneumatics
from configs.components.autoAim import AutoAim

class Autonomous(AutonomousStateMachine):
    """Creates the autonomous code"""
    time = 1.4
    MODE_NAME = "Basic Autonomous"
    DEFAULT = True
    driveTrain: DriveTrain
    shooter: ShooterLogic
    shooterMotors: ShooterMotorCreation
    pneumatics: Pneumatics
    autoAim: AutoAim
    drive_speed = tunable(.25)

    """call aas here as new state"""

    @state(first = True)
    def shoot(self):
        """Aims the turret and fires"""
        self.autoAim.aimAndShoot()
        self.next_state('shooter_wait')

    @state
    def engage_shooter(self):
        """Starts shooter and fires"""
        self.pneumatics.deployLoader()
        self.shooter.shootBalls()
        self.next_state('shooter_wait')

    @state
    def shooter_wait(self):
        """Waits for shooter to finish, then next state"""
        if self.shooter.current_state == 'idling':
            self.next_state_now('drive_backwards')

    @timed_state(duration = time, next_state = 'turn')
    def drive_backwards(self):
        """Drives the bot backwards for a time"""
        self.driveTrain.setTank(self.drive_speed, self.drive_speed)

    @timed_state(duration = time, next_state = 'stop')
    def turn(self):
        """Turns for a time"""
        self.driveTrain.setTank(-self.drive_speed, self.drive_speed)

    @state(must_finish = True)
    def stop(self):
        """Stops driving bot"""
        self.driveTrain.setTank(0, 0)
        self.done()
