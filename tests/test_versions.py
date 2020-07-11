import os
import sys

sys.path.insert(0, os.path.abspath("."))

import pyheif


def test_libheif_version():
    version = pyheif.libheif_version()
    assert version != ""


def test_pyheif_version():
    with open("pyheif/data/version.txt") as f:
        expected_version = f.read().strip()

    version = pyheif.__version__
    assert expected_version == version
