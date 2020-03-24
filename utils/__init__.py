from os.path import dirname, basename, isfile, join
import os
import glob

component_directory = dirname(__file__) + os.path.sep + '..' + os.path.sep + 'components'
directory = join(component_directory, "*.py")
modules = glob.glob(directory) # Takes a directory and returns a list of identical path names. Because directory ends in '*.py', all python files in this directory are added to the list
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not os.path.basename(f).startswith('_')]
