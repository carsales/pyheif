from _libheif_cffi import ffi, lib
from .reader import read_heif
from .writer import write_heif

__version__ = '0.5.0'

def libheif_version():
    version = lib.heif_get_version()
    version = ffi.string(version).decode()
    return version
