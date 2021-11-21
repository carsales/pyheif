import gc
import glob
import io
from pathlib import Path

import piexif
from PIL import Image, ImageCms
import pyheif.reader
import pytest


heic_files = list(Path().glob("tests/images/**/*.heic"))
hif_files = list(Path().glob("tests/images/**/*.HIF"))
avif_files = list(Path().glob("tests/images/**/*.avif"))
heif_files = heic_files + hif_files + avif_files


@pytest.mark.parametrize("path", heif_files)
def test_check(path):
    filetype = pyheif.check(path)
    assert pyheif.heif_filetype_no != filetype


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_path(path):
    d = pyheif.reader._get_bytes(path)
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_file_name(path):
    d = pyheif.reader._get_bytes(str(path))
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_file_object(path):
    with open(path, "rb") as f:
        d = pyheif.reader._get_bytes(f)
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_bytes(path):
    with open(path, "rb") as f:
        d = pyheif.reader._get_bytes(f.read())
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_bytes(path):
    with open(path, "rb") as f:
        d = pyheif.reader._get_bytes(bytearray(f.read()))
    assert d == path.read_bytes()


@pytest.fixture(scope="session", params=heif_files)
def heif_file(request):
    return pyheif.read(request.param)


def test_check_heif_propreties(heif_file):
    assert heif_file is not None
    width, height = heif_file.size
    assert width > 0
    assert height > 0
    assert len(heif_file.data) > 0


def test_read_exif_metadata(heif_file):
    for m in heif_file.metadata or []:
        if m["type"] == "Exif":
            exif_dict = piexif.load(m["data"])
            assert "0th" in exif_dict
            assert len(exif_dict["0th"]) > 0
            assert "Exif" in exif_dict
            assert len(exif_dict["Exif"]) > 0


def test_read_icc_color_profile(heif_file):
    if heif_file.color_profile and heif_file.color_profile["type"] in ["prof", "rICC"]:
        profile = io.BytesIO(heif_file.color_profile["data"])
        cms = ImageCms.getOpenProfile(profile)


def test_read_pillow_frombytes(heif_file):
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )


@pytest.mark.parametrize("path", heif_files)
def test_open_and_load(path):
    heif_file = pyheif.open(path)
    assert heif_file.size[0] > 0
    assert heif_file.size[1] > 0
    assert heif_file.has_alpha is not None
    assert heif_file.mode is not None
    assert heif_file.bit_depth is not None

    assert heif_file.data is None
    assert heif_file.stride is None

    if path.name == "arrow.heic":
        assert heif_file.metadata
        assert heif_file.color_profile

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


@pytest.mark.parametrize("path", heif_files)
def test_open_and_load_data_not_collected(path):
    data = path.read_bytes()
    heif_file = pyheif.open(data)

    # heif_file.load() should work even if there is no other refs
    # to the source data.
    data = None
    gc.collect()

    heif_file.load()
