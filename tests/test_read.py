import gc
import glob
import io
from pathlib import Path

import piexif
from PIL import Image, ImageCms
import pyheif
import pytest


heif_files = list(Path().glob("tests/images/**/*.heic"))
hif_files = list(Path().glob("tests/images/**/*.HIF"))


@pytest.fixture(scope="session", params=heif_files)
def heif_file(request):
    return pyheif.read(request.param)


def read_and_quick_check_heif(source):
    heif_file = pyheif.read(source)
    assert heif_file is not None
    width, height = heif_file.size
    assert width > 0
    assert height > 0
    assert len(heif_file.data) > 0


def create_pillow_image(heif_file):
    return Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )


@pytest.mark.parametrize("path", heif_files)
def test_check_filetype(path):
    filetype = pyheif.check(path)
    assert pyheif.heif_filetype_no != filetype


@pytest.mark.parametrize("path", heif_files)
def test_read_file_names(path):
    read_and_quick_check_heif(str(path))


@pytest.mark.parametrize("path", heif_files)
def test_read_paths(path):
    read_and_quick_check_heif(path)


@pytest.mark.parametrize("path", heif_files)
def test_read_file_objects(path):
    with open(path, "rb") as f:
        read_and_quick_check_heif(f)


@pytest.mark.parametrize("path", heif_files)
def test_read_bytes(path):
    with open(path, "rb") as f:
        read_and_quick_check_heif(f.read())


@pytest.mark.parametrize("path", heif_files)
def test_read_bytearrays(path):
    with open(path, "rb") as f:
        read_and_quick_check_heif(bytearray(f.read()))


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
    image = create_pillow_image(heif_file)
    # image.save(f"{fn}.png")


@pytest.mark.parametrize("path", hif_files)
def test_read_10_bit(path):
    heif_file = pyheif.read(path)
    image = create_pillow_image(heif_file)


@pytest.mark.parametrize("path", heif_files + hif_files)
def test_open_and_load(path):
    heif_file = pyheif.open(path)
    assert heif_file.size[0] > 0
    assert heif_file.size[1] > 0
    assert heif_file.has_alpha is not None
    assert heif_file.mode is not None
    assert heif_file.bit_depth is not None

    assert heif_file.data is None
    assert heif_file.stride is None

    if path.name == 'arrow.heic':
        assert heif_file.metadata
        assert heif_file.color_profile

    heif_file.load()
    assert heif_file.data is not None
    assert heif_file.stride is not None
    assert len(heif_file.data) >= heif_file.stride * heif_file.size[1]
    assert type(heif_file.data[:100]) == bytes


@pytest.mark.parametrize("path", heif_files + hif_files)
def test_open_and_load_data_collected(path):
    data = path.read_bytes()
    heif_file = pyheif.open(data)
    
    # heif_file.load() should work even if there is no other refs 
    # to the source data.
    data = None
    gc.collect()

    heif_file.load()
