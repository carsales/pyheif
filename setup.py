import os
import codecs
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


# with open("pyheif/data/version.txt") as f:
#    version = f.read().strip()
version = get_version("pyheif/__init__.py")

setup(
    name="pyheif",
    version=version,
    packages=["pyheif"],
    package_data={"pyheif": ["data/*"]},
    install_requires=["cffi>=1.0.0"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["libheif/libheif_build.py:ffibuilder"],
    author="David Poirier",
    author_email="david-poirier-csn@users.noreply.github.com",
    description="Python 3.6+ interface to libheif library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">= 3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="heif heic",
    url="https://github.com/david-poirier-csn/pyheif",
)
