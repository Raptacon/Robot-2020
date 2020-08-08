import networktable

class AutoAim(AutonomousStateMachine):
    compatString = ["doof"]
    time = 0.1
    driveTrain: DriveTrain
    shooter: ShooterLogic
    drive_speed_left = tunable(.05)
    drive_speed_right = tunable(-.05)
    minAimOffset = .5;
    table: networktable

    @state(first = True)
    def start(self):
        """should add check if limelight even sees it to auto send it to stop in case hit or pressed accidentally"""
        table.getTable("limelight")
        tx = table("tx")
        if tx > minAimOffset:
            self.next_state_now("adjust_self_left")
        elif tx < -1*minAimOffset:
           self.next_state_now("adjust_self_right")
        elif tx < minAimOffset and tx > -1*minAimOffset:
            self.next_state_now("stop_shoot")
        else:
            self.next_state_now("stop")
            
         
    @timed_state(duration = time, next_state = "start")
    def adjust_self_left(self):
        """Drives the bot backwards for a time"""
        self.driveTrain.setTank(self.drive_speed_left, self.drive_speed_right)
    
    @timed_state(duration = time, next_state = "start")
    def adjust_self_right(self):
        """Drives the bot backwards for a time"""
        self.driveTrain.setTank(self.drive_speed_right, self.drive_speed_left)

    @state(must_finish = True)
    def stop_shoot(self):
        #stop
        self.driveTrain.setTank(0, 0)  
        #shoot
        self.shooter.shootBalls()
  
    @state(must_finish = True)
    def stop(self):
    