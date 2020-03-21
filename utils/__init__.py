from os.path import dirname, basename, isfile, join
import os
import glob

component_directory = dirname(__file__) + os.path.sep + '..' + os.path.sep + 'components'
directory = join(component_directory, "*.py")
modules = glob.glob(directory)
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not os.path.basename(f).startswith('_')]