"""
Class that uses inputs, particularly from the limelight,
to align the bot to a target
"""
#from components.driveTrain import DriveTrain
from components.limelight import Limelight
from magicbot import StateMachine, state, timed_state, tunable

class Align(StateMachine):
    #drivetrain: DriveTrain

    def setup(self):
        self.x = tunable(0)
        pass

    def alignToX(self):
        pass

    def alignToY(self):
        pass

    def beginAlign(self):
        pass
        #self.engage()
    
    @timed_state(first=True, duration = 1, next_state = 'nextOtherState')
    def runAlignLoop(self):
        while True:
            print("align")
            if self.x != 0:
                self.next_state('stopAlign')

    @state
    def stopAlign(self):
        while True:
            print("stopping")

    @state
    def testOtherState(self):
        while True:
            print("time exceded")