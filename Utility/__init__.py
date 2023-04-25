

#Code from https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
#from os.path import dirname, basename, isfile, join
#import glob
#
#modules = glob.glob(join(dirname(__file__), "*.py"))
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

#Actually works
from .GraphUtil import *
from .FileUtil import *

#test utility
from .TestUtil import *
from .TimeUtil import *

from .IPSMagUtil import *
from .SMSMagUtil import *

from .LockinUtil import *
from .LockinUtil_big import*#7280 Lockin
from .LockinUtil_small import*#7265 Lockin
from .LockinUtil_SRS import*