from sys import argv as args
import os
from os.path import dirname
import json
import subprocess

arg_count = len(args)

if arg_count == 1:
    print("ArgumentError: No arguments given.")
    # add print here for arg options/descps
    exit(1)

if arg_count >= 3:
    print("ArgumentError: Too many arguments for action.")
    # add print here for arg options/descps
    exit(1)

action = args[1]

configFile = dirname(__file__) + os.path.sep + '_commands.json'
with open(configFile) as file:
    loadedFile = json.load(file)

for key, raw_command in loadedFile.items():
    if action == key:
        command = raw_command.replace("/", os.path.sep)
        executed_action = subprocess.check_output(command).decode('utf-8')
        print(executed_action)
