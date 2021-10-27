import os
import sys

sys.path.insert(0, os.path.abspath("."))

import pyheif


def test_libheif_version():
    version = pyheif.libheif_version()
    assert version != ""


def test_pyheif_version():
    version = pyheif.__version__
    assert version != ""