from networktables import NetworkTables as networktable
from magicbot import StateMachine, tunable
from magicbot.state_machine import state, timed_state
from components.driveTrain import DriveTrain
from components.autoShoot import AutoShoot

import logging as log


class AutoAlign(StateMachine):
    """
    Puts the limelight (not necessarily the entirely robot)
    roughly perpendicular to any target the limelight
    currently has in its view.
    """

    compatString = ["doof"]
    time = 0.1
    driveTrain: DriveTrain

    # Auto Align variables
    shootAfterComplete = False
    drive_speed_left = tunable(.17)
    drive_speed_right = tunable(-.17)
    maxAimOffset = 2

    # PID
    P = 0
    I = 0
    D = 0
    speed = 0
    integral = 0
    preverror = 0

    limeTable = networktable.getTable("limelight")

    autoShoot: AutoShoot

    def setShootAfterComplete(self, input: bool):
        self.shootAfterComplete = input
        return self.shootAfterComplete

    def toggleShootAfterComplete(self):
        if self.shootAfterComplete:
            self.shootAfterComplete = False
        else:
            self.shootAfterComplete = True
        return self.shootAfterComplete

    @state(first=True)
    def start(self):

        # If limelight can see something
        self.tx = self.limeTable.getNumber("tx", -50)
        if self.tx != -50 or self.tx != 0:
            # "-50" is the default value, so if that is returned,
            # nothing should be done because there is no connection.
            tx = self.limeTable.getNumber("tx", -50)
            if tx != -50 and tx != 0:
                if tx > self.maxAimOffset:
                    self.speed = self.calc_PID(tx)
                    self.next_state_now("adjust_self_right")

                elif tx < -1 * self.maxAimOffset:
                    self.speed = self.calc_PID(tx)
                    self.next_state_now("adjust_self_left")

                # If the horizontal offset is within the given tolerance,
                # finish.
                elif tx < self.maxAimOffset and tx > -1 * self.maxAimOffset:
                    if self.shootAfterComplete:
                        self.autoShoot.engage()

        else:
            log.error("Limelight: No Valid Targets")

    @timed_state(duration=time, next_state="start")
    def adjust_self_right(self):
        """Turns the bot right"""
        self.driveTrain.setTank(self.speed, -1 * self.speed)

    @timed_state(duration=time, next_state="start")
    def adjust_self_left(self, speed):
        """Turns the bot left"""
        self.driveTrain.setTank(-1 * self.speed, self.speed)

    def calc_PID(self, error):
        """
        Uses PID values defined in init section to give a power output for
        the drivetrain. .02 is the amount of time assumed to have passed.
        """
        self.integral = self.integral + error * .02
        setspeed = self.P * (error) + self.D * (error - self.preverror)
        + self.I * (self.integral * .02)
        self.preverror = error
        return setspeed

    def reset_integral(self):
        self.integral = 0
