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
        assert heif_file.brand != pyheif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


def test_read_paths():
    for fn in Path().glob("tests/images/**/*.heic"):
        heif_file = pyheif.read(fn)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pyheif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


def test_read_file_objects():
    for fn in Path().glob("tests/images/**/*.heic"):
        with open(fn, "rb") as f:
            heif_file = pyheif.read(f)
            assert heif_file is not None
            width, height = heif_file.size
            assert width > 0
            assert height > 0
            assert heif_file.brand != pyheif.constants.heif_brand_unknown_brand
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
            assert heif_file.brand != pyheif.constants.heif_brand_unknown_brand
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
            assert heif_file.brand != pyheif.constants.heif_brand_unknown_brand
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
