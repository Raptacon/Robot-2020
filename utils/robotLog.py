import os
import wpilib
from os.path import dirname
from datetime import datetime

def __getRunInfo():
    """
    Gets essential runtime information for creating a log entry.
    """

    commit_hash = os.popen('git rev-parse HEAD').readline().strip()
    branch = os.popen('git branch --show-current')
    branch_name = branch.readline().strip()
    git_type = 'branch'
    runtime_version = branch_name
    if not branch_name:
        tag = os.popen('git describe --tags')
        tag_name = tag.readline().strip()
        git_type = 'version'
        runtime_version = tag_name

    # Determine simulation status
    if wpilib.RobotBase.isSimulation():
        is_simulation = True
    else:
        is_simulation = False

    # Get date info
    currentDT = datetime.now()
    date = currentDT.strftime("%a, %b %d, %Y")
    time = currentDT.strftime("%I:%M:%S %p")

    return is_simulation, runtime_version, git_type, commit_hash, date, time

def __createEntry(is_sim, version, git_type, commit, date, time):
    """
    Creates a logged entry based on runtime information.
    Requires info arguments.
    """

    log_dir = dirname(__file__) + os.path.sep + '..' + os.path.sep + '_system_utils' + os.path.sep + '_robot_log.txt'
    if is_sim:
        run_type = "Simulation"
    elif not is_sim:
        run_type = "Deploy"
    with open(log_dir, 'a') as txt_file:
        txt_file.write(
            f"{run_type} with {git_type} '{version}' (commit hash {commit}) on {date} at {time} \n"
        )

def log(deploys = True, simulations = False):
    """
    Log a robot deploy/simulation.

    :param deploys: If set to True, write deploys to log file.

    :param simulations: If set to True, write simulations to log file.
    """

    is_simulation, version, git_type, commit, date, time = __getRunInfo()

    if simulations and is_simulation:
        __createEntry(is_simulation, version, git_type, commit, date, time)
    elif deploys and not is_simulation:
        __createEntry(is_simulation, version, git_type, commit, date, time)
