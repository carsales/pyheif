from _libheif_cffi import ffi, lib
from .constants import *
from .error import HeifError


class HeifFile:
    def __init__(self, *,
            mode, size, data):
        self.mode=mode
        self.size=size
        self.data=data


def read_heif(fp):
    if isinstance(fp, str):
        with open(fp, 'rb') as f:
            d = f.read()
    elif isinstance(fp, bytes):
        d = fp
    elif isinstance(fp, bytearray):
        d = bytes(fp)
    elif hasattr(fp, 'read'):
        d = fp.read()
    else:
        raise ArgumentException('Input must be file name, bytes, byte array, or file-like object')

    result = _read_heif_bytes(d)
    return result


def _read_heif_bytes(d):
    ctx = lib.heif_context_alloc()
    try: 
        result = _read_heif_context(ctx, d)
    except:
        raise
    finally:
        lib.heif_context_free(ctx)
    return result


def _read_heif_context(ctx, d):
    error = lib.heif_context_read_from_memory(ctx, d, len(d), ffi.NULL)
    if error.code != 0:
        raise HeifError(code=error.code, subcode=error.subcode, message=ffi.string(error.message).decode())

    p_handle = ffi.new('struct heif_image_handle **');
    error = lib.heif_context_get_primary_image_handle(ctx, p_handle);
    if error.code != 0:
        raise HeifError(code=error.code, subcode=error.subcode, message=ffi.string(error.message).decode())
    handle = p_handle[0]

    try:
        result = _read_heif_handle(handle)
    except:
        raise
    finally:
        lib.heif_image_handle_release(handle)
    return result


def _read_heif_handle(handle):
    width = lib.heif_image_handle_get_width(handle)
    height = lib.heif_image_handle_get_height(handle)
    size = (width, height)
    
    alpha = lib.heif_image_handle_has_alpha_channel(handle)
    mode = 'RGB' if alpha==0 else 'RGBA'

    p_img = ffi.new('struct heif_image **');
    error = lib.heif_decode_image(
            handle, p_img, heif_colorspace_RGB, 
            heif_chroma_interleaved_RGB if mode=='RGB' else heif_chroma_interleaved_RGBA, 
            ffi.NULL)
    if error.code != 0:
        raise HeifError(code=error.code, subcode=error.subcode, message=ffi.string(error.message).decode())
    img = p_img[0]
    
    try:
        data = _read_heif_image(img, height)
    except:
        raise
    finally:
        lib.heif_image_release(img)

    heif_file = HeifFile(mode=mode, size=size, data=data)
    return heif_file


def _read_heif_image(img, height):
    p_stride = ffi.new('int *')
    p_data = lib.heif_image_get_plane_readonly(img, heif_channel_interleaved, p_stride);
    stride = p_stride[0]

    data_length = height * stride
    data_buffer = ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)

    return data

