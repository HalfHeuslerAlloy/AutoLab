

#Code from https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
#from os.path import dirname, basename, isfile, join
#import glob
#
#modules = glob.glob(join(dirname(__file__), "*.py"))
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

#Actually works
from .Dummy import *
from .DSP_7265 import *
from .Keithley2400 import *
from .DSP_7280 import *
from .IPS120 import *
from .SMS120C import *
from .Arroyo4300 import *
from .SR830 import *
from .lakeshore350 import*
from .lakeshore218 import *
from .Keithley6221 import *