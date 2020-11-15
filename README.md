# pyheif
Python 3.6+ interface to [libheif](https://github.com/strukturag/libheif) library using CFFI

*Note*: currently only reading is supported.

## Installation

### Simple installation - Linux (installs manylinux2014 wheel, doesn't work with Alpine)
```
pip install --upgrade pip
pip install pyheif
```

### Installing from source - MacOS
```
brew install libffi libheif
pip install git+https://github.com/carsales/pyheif.git
```

### Installing from source - Linux
```
apt install libffi libheif-dev libde265-dev
```
or
```
yum install libffi libheif-devel libde265-devel
```
then
```
pip install git+https://github.com/carsales/pyheif.git
```

### Installing from source - Windows
```
Sorry, not going to happen!
```

## Usage

The `pyheif.read(path_or_bytes)` function can be used to read a HEIF encoded file. It can be passed any of the following:

* A string path to a file on disk
* A `pathlib.Path` path object
* A Python `bytes` or `bytearray` object containing HEIF content
* A file-like object with a `.read()` method that returns bytes

It returns a `HeifFile` object.

```python
import pyheif

# Using a file path:
heif_file = pyheif.read("IMG_7424.HEIC")
# Or using bytes directly:
heif_file = pyheif.read(open("IMG_7424.HEIC", "rb").read())
```

### The HeifFile object

The returned `HeifFile` has the following properties:

* `mode` - the image mode, e.g. "RGB" or "RGBA"
* `size` - the size of the image as a `(width, height)` tuple of integers
* `data` - the raw decoded file data, as bytes
* `metadata` - a list of metadata dictionaries
* `color_profile` - a color profile dictionary
* `stride` - the number of bytes in a row of decoded file data
* `bit_depth` - the number of bits in each component of a pixel

### Converting to a Pillow Image object

If your HEIF file contains an image that you would like to manipulate, you can do so using the [Pillow](https://pillow.readthedocs.io/) Python library. You can convert a `HeifFile` to a Pillow image like so:

```python
from PIL import Image
import pyheif

heif_file = pyheif.read("IMG_7424.HEIC")
image = Image.frombytes(
    heif_file.mode, 
    heif_file.size, 
    heif_file.data,
    "raw",
    heif_file.mode,
    heif_file.stride,
    )
```

*Note*: the `mode` property is passed twice - once to the `mode` argument of the `frombytes` method, and again to the `mode` argument of the `raw` decoder.

You can now use any Pillow method to manipulate the file. Here's how to convert it to JPEG:

```python
image.save("IMG_7424.jpg", "JPEG")
```
