from sys import argv as args
import os
from os.path import dirname
import json

arg_count = len(args)

if arg_count == 1:
    print("ArgumentError: No arguments given.")
    print("Actions: ")
    # add print here for arg options/descps
    exit(1)

if arg_count >= 3:
    print("ArgumentError: Too many arguments for action.")
    print("Actions: ")
    # add print here for arg options/descps
    exit(1)

action = args[1]

print(action)

configFile = dirname(__file__) + os.path.sep + '_commands.json'
with open(configFile) as file:
    loadedFile = json.load(file)

print(loadedFile)
