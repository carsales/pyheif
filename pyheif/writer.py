import warnings

import _libheif_cffi
from . import constants as _constants
from . import error as _error


class RawFile:
    def _init__(self, *, size, data, mode, depth):
        self.size = size
        self.data = data
        self.mode = mode
        self.depth = depth


def write(raw, fmt, quality=50, lossless=False):
    warnings.warn("write is experimental, you probably shouldn't use it!")

    if fmt not in ["HEIC", "AVIF"]:
        raise ValueError("'fmt' must be either 'HEIC' or 'AVIF'")

    context = _libheif_cffi.lib.heif_context_alloc()

    width, height = raw.size
    colorspace = _constants.heif_colorspace_RGB
    chroma = _constants.heif_chroma_interleaved_RGB
    depth = raw.depth
    if fmt == "HEIC":
        compression = _constants.heif_compression_HEVC
    elif fmt == "AVIF":
        compression = _constants.heif_compression_AV1

    p_image = _libheif_cffi.ffi.new("struct heif_image_handle *")
    image = p_image[0]
    error = _libheif_cffi.lib.heif_image_create(
        width, height, colorspace, chroma, image
    )
    error = _libheif_cffi.lib.heif_image_add_plane(
        image, _constants.heif_channel_interleaved, width, height, depth
    )
    encoder_descriptors = _libheif_cffi.ffi.new("const heif_encoder_descriptor *")
    _libheif_cffi.lib.heif_context_get_encoder_descriptors(
        context, compression, _libheif_cffi.ffi.NULL, encoder_descriptors, 5
    )

    p_encoder = _libheif_cffi.ffi.new("heif_encoder *")
    encoder = p_encoder[0]
    error = _libheif_cffi.lib.heif_context_get_encoder(
        context, encoder_descriptors[0], encoder
    )
    _libheif_cffi.lib.heif_encoder_set_lossy_quality(encoder, quality)
    _libheif_cffi.lib.heif_encoder_set_lossless(encoder, lossless)

    p_handle = _libheif_cffi.ffi.new("struct heif_image_handle *")
    handle = p_handle[0]
    error = _libheif_cffi.lib.heif_context_encode_image(
        context, image, encoder, _libheif_cffi.ffi.NULL, handle
    )

    _libheif_cffi.lib.heif_encoder_release(encoder)
    _libheif_cffi.lib.heif_image_release(image)
    _libheif_cffi.lib.heif_context_free(context)

    return image
