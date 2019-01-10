import glob
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import pyheif


def test_read_file_names():
    for fn in glob.glob('tests/images/*.heic'):
        heif_file = pyheif.read_heif(fn)
        assert(heif_file is not None)
        assert(heif_file.mode in ['RGB', 'RGBA'])
        width, height = heif_file.size
        assert(width > 0)
        assert(height > 0)
        assert(len(heif_file.data) > 0)


def test_read_file_objects():
    for fn in glob.glob('tests/images/*.heic'):
        with open(fn, 'rb') as f:
            heif_file = pyheif.read_heif(f)
            assert(heif_file is not None)
            assert(heif_file.mode in ['RGB', 'RGBA'])
            width, height = heif_file.size
            assert(width > 0)
            assert(height > 0)
            assert(len(heif_file.data) > 0)
        
def test_read_file_bytes():
    for fn in glob.glob('tests/images/*.heic'):
        with open(fn, 'rb') as f:
            d = f.read()
            heif_file = pyheif.read_heif(d)
            assert(heif_file is not None)
            assert(heif_file.mode in ['RGB', 'RGBA'])
            width, height = heif_file.size
            assert(width > 0)
            assert(height > 0)
            assert(len(heif_file.data) > 0)
        
def test_read_file_bytes():
    for fn in glob.glob('tests/images/*.heic'):
        with open(fn, 'rb') as f:
            d = f.read()
            heif_file = pyheif.read_heif(d)
            assert(heif_file is not None)
            assert(heif_file.mode in ['RGB', 'RGBA'])
            width, height = heif_file.size
            assert(width > 0)
            assert(height > 0)
            assert(len(heif_file.data) > 0)

def test_read_file_bytearrays():
    for fn in glob.glob('tests/images/*.heic'):
        with open(fn, 'rb') as f:
            d = f.read()
            d = bytearray(d)
            heif_file = pyheif.read_heif(d)
            assert(heif_file is not None)
            assert(heif_file.mode in ['RGB', 'RGBA'])
            width, height = heif_file.size
            assert(width > 0)
            assert(height > 0)
            assert(len(heif_file.data) > 0)
 
