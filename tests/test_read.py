import gc
import glob
import io
import os
import pprint
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))

import piexif
from PIL import Image, ImageCms
import pyheif


def test_check_filetype():
    for fn in Path().glob("tests/images/**/*.heic"):
        filetype = pyheif.check(fn)
        assert pyheif.heif_filetype_no != filetype


def test_read_file_names():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert len(heif_file.data) > 0


def test_read_paths():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert len(heif_file.data) > 0


def test_read_file_objects():
    for fn in Path().glob("tests/images/**/*.heic"):
        with open(fn, "rb") as f:
            heif_file = pyheif.read(f)
            assert heif_file is not None
            width, height = heif_file.size
            assert width > 0
            assert height > 0
            assert len(heif_file.data) > 0


def test_read_bytes():
    for fn in Path().glob("tests/images/**/*.heic"):
        with open(fn, "rb") as f:
            d = f.read()
            heif_file = pyheif.read(d)
            assert heif_file is not None
            width, height = heif_file.size
            assert width > 0
            assert height > 0
            assert len(heif_file.data) > 0


def test_read_bytearrays():
    for fn in Path().glob("tests/images/**/*.heic"):
        with open(fn, "rb") as f:
            d = f.read()
            d = bytearray(d)
            heif_file = pyheif.read(d)
            assert heif_file is not None
            width, height = heif_file.size
            assert width > 0
            assert height > 0
            assert len(heif_file.data) > 0


def test_read_exif_metadata():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        for m in heif_file.metadata or []:
            if m["type"] == "Exif":
                exif_dict = piexif.load(m["data"])
                assert "0th" in exif_dict
                assert len(exif_dict["0th"]) > 0
                assert "Exif" in exif_dict
                assert len(exif_dict["Exif"]) > 0


def test_read_icc_color_profile():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        if heif_file.color_profile and heif_file.color_profile["type"] in [
            "prof",
            "rICC",
        ]:
            profile = io.BytesIO(heif_file.color_profile["data"])
            cms = ImageCms.getOpenProfile(profile)


def test_read_pillow_frombytes():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        # image.save(f"{fn}.png")


def test_read_10_bit():
    for fn in Path().glob("tests/images/**/*.HIF"):
        heif_file = pyheif.read(fn)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )


def test_open_and_load():
    last_metadata = None
    last_color_profile = None
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.open(fn)
        assert heif_file.size[0] > 0
        assert heif_file.size[1] > 0
        assert heif_file.has_alpha is not None
        assert heif_file.mode is not None
        assert heif_file.bit_depth is not None

        assert heif_file.data is None
        assert heif_file.stride is None

        if heif_file.metadata:
            last_metadata = heif_file.metadata[0]
        if heif_file.color_profile:
            last_color_profile = heif_file.color_profile

        res = heif_file.load()
        assert heif_file is res
        assert heif_file.data is not None
        assert heif_file.stride is not None
        assert len(heif_file.data) >= heif_file.stride * heif_file.size[1]
        assert type(heif_file.data[:100]) == bytes

        # Subsequent calls don't change anything
        res = heif_file.load()
        assert heif_file is res
        assert heif_file.data is not None
        assert heif_file.stride is not None

    # Check at least one file has it
    assert last_metadata is not None
    assert last_color_profile is not None


def test_open_and_load_data_collected():
    for fn in Path().glob("tests/images/**/*.heic"):
        data = fn.read_bytes()
        heif_file = pyheif.open(data)
        
        # heif_file.load() should work even if there is no other refs 
        # to the source data.
        data = None
        gc.collect()

        heif_file.load()
