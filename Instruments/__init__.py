

#Code from https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
#from os.path import dirname, basename, isfile, join
#import glob
#
#modules = glob.glob(join(dirname(__file__), "*.py"))
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

#Actually works
# =============================================================================
# AUTOLAB CODE MODULES
# =============================================================================
from .Dummy import *

# =============================================================================
# LOCKIN MODULES
# =============================================================================
from .DSP_7265 import *
from .DSP_7280 import *
from .SR830 import *
from .SR530 import *

# =============================================================================
# KEITHLEY MODULES
# =============================================================================

from .Keithley2400 import *
from .Keithley6221 import *
from .Keithley236 import*

# =============================================================================
# TEMPERATURE CONTROL MODULES
# =============================================================================
from .lakeshore350 import*
from .lakeshore218 import *
from .OI_503 import *

# =============================================================================
# MAGNET SUPPLY MODULES
# =============================================================================
from .IPS120 import *
from .SMS120C import *

# =============================================================================
# OTHER MODULES
# =============================================================================

from .Arroyo4300 import *
from .OI_ILM import*


