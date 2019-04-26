from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyheif',
    version='0.3.2',
    packages=find_packages(),
    install_requires=['cffi>=1.0.0'],
    setup_requires=['cffi>=1.0.0'],
    cffi_modules=['libheif_build.py:ffibuilder'],
    author='David Poirier',
    author_email='david-poirier-csn@users.noreply.github.com',
    description='Python 3 interface to libheif library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux'
    ],
    keywords='heif',
    url='https://github.com/david-poirier-csn/pyheif'
)
