import glob
import io
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import piexif
import pyheif
from PIL import ImageCms


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

def test_read_file_exif_metadata():
    for fn in glob.glob('tests/images/*.heic'):
        heif_file = pyheif.read_heif(fn)
        for m in heif_file.metadata or []:
            if m['type']=='Exif':
                exif_dict = piexif.load(m['data'])
                assert('0th' in exif_dict)
                assert(len(exif_dict['0th']) > 0)
                assert('Exif' in exif_dict)
                assert(len(exif_dict['Exif']) > 0)

def test_read_file_icc_color_profile():
    for fn in glob.glob('tests/images/*.heic'):
        heif_file = pyheif.read_heif(fn)
        if heif_file.color_profile and heif_file.color_profile['type'] in ['prof','rICC']:
            profile = io.BytesIO(heif_file.color_profile['data'])
            cms = ImageCms.getOpenProfile(profile)

