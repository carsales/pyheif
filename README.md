# pyheif
Python 3.6+ interface to [libheif](https://github.com/strukturag/libheif) library using CFFI

## Installation

### Simple installation (requires libheif + libde265 + x265)
```pip install pyheif```

### Installing from source - MacOS
```
brew install libffi libheif
pip install git+https://github.com/david-poirier-csn/pyheif.git
```

### Installing from source - Linux
```
apt install libffi libheif-dev libde265-dev x265-dev
```
or
```
yum install libffi libheif-devel libde265-devel x265-devel
```
then
```
pip install git+https://github.com/david-poirier-csn/pyheif.git
```

### Installing from source - Windows
```
Sorry, not going to happen!
```

## Usage

The `pyheif.read_heif(path_or_bytes)` function can be used to read a HEIF encoded file. It can be passed any of the following:

* A string path to a file on disk
* A `pathlib.Path` path object
* A Python `bytes` or `bytearray` object containing HEIF content
* A file-like object with a `.read()` method that returns bytes

It returns a `HeifFile` object.

```python
import pyheif

# Using a file path:
heif_file = pyheif.read_heif("IMG_7424.HEIC")
# Or using bytes directly:
heif_file = pyheif.read_heif(open("IMG_7424.HEIC", "rb").read())
```

### The HeifFile object

The returned `HeifFile` has the following properties:

* `heif_file.mode` - the image mode, e.g. "RGB"
* `heif_file.size` - the size of the image as a `(width, height)` tuple of integers
* `heif_file.data` - the raw decoded file data, as bytes
* `heif_file.metadata` - a list of metadata dictionaries
* `heif_file.color_profile` - a color profile dictionary

### Converting to a Pillow Image object

If your HEIF file contains an image that you would like to manipulate, you can do so using the [Pillow](https://pillow.readthedocs.io/) Python library. You can convert a `heif_file` to a Pillow image like so:

```python
from PIL import Image
import pyheif

heif_file = pyheif.read_heif("IMG_7424.HEIC")
image = Image.frombytes(mode=heif_file.mode, size=heif_file.size, data=heif_file.data)
```

You can now use any Pillow method to manipulate the file. Here's how to convert it to JPEG:

```python
image.save("IMG_7424.jpg", "JPEG")
```
