import glob
import os
from os.path import dirname, basename, isfile, join

modules = glob.glob(join(dirname(__file__), '*.py')) # Takes a directory and returns a list of identical path names. Because directory ends in '*.py', all python files in this directory are added to the list
factory_modules = [basename(f)[:-3] for f in modules if isfile(f) and not os.path.basename(f).startswith('_')]

# NOTE This is only for flake8
def dummy():
    pass
