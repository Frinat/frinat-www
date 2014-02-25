import warnings
import logging
import sys

if not sys.warnoptions:
    warnings.simplefilter('default', DeprecationWarning)
    warnings.filterwarnings('ignore', '.*', DeprecationWarning, 'mptt.models', 305)
    logging.captureWarnings(True)
    sys.warnoptions.append('ignore::DeprecationWarning')

from .common import *
