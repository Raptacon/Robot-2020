import os
from time import sleep

os.popen('git checkout master')
sleep(10)
os.popen('git checkout RoboWindow')
