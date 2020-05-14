import os
from time import sleep

os.popen('git checkout master')

if os.popen('git branch --show-current').readline().strip() == 'master':
    print(os.popen('git branch --show-current').readline().strip())
    sleep(2)
    os.popen('git checkout RoboWindow')
