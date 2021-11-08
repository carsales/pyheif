from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("pyheif/data/version.txt") as f:
    version = f.read().strip()

setup(
    name="pyheif",
    version=version,
    packages=["pyheif"],
    package_data={"pyheif": ["data/*"]},
    install_requires=["cffi>=1.0.0"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["libheif/libheif_build.py:ffibuilder"],
    author="Anthony Paes",
    author_email="ant32bit-carsales@users.noreply.github.com",
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
    url="https://github.com/carsales/pyheif",
)
