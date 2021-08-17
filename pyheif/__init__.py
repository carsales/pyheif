import os

import _libheif_cffi

from .constants import *
from .reader import *
from .writer import *

# version_path = os.path.dirname(os.path.abspath(__file__)) + "/data/version.txt"
# with open(version_path) as f:
#    __version__ = f.read().strip()
__version__ = "0.5.1"


def libheif_version():
    version = _libheif_cffi.lib.heif_get_version()
    version = _libheif_cffi.ffi.string(version).decode()
    return version
