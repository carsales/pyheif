from _libheif_cffi import ffi, lib
from .constants import *
from .error import HeifError


class HeifFile:
    def __init__(self, *,
            mode, size, data, metadata, color_profile):
        self.mode=mode
        self.size=size
        self.data=data
        self.metadata=metadata
        self.color_profile=color_profile


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

    metadata = _read_metadata(handle)    
    color_profile = _read_color_profile(handle)

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

    heif_file = HeifFile(
            mode=mode, size=size, data=data, metadata=metadata, color_profile=color_profile)
    return heif_file


def _read_metadata(handle):

    block_count = lib.heif_image_handle_get_number_of_metadata_blocks(handle, ffi.NULL)
    if block_count == 0:
        return

    metadata = []
    ids = ffi.new('heif_item_id[]', block_count)
    lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, ffi.NULL, ids, block_count)
    for i in range(len(ids)):
        metadata_type = lib.heif_image_handle_get_metadata_type(handle, ids[i])
        metadata_type = ffi.string(metadata_type).decode()
        data_length = lib.heif_image_handle_get_metadata_size(handle, ids[i])
        p_data = ffi.new('char[]', data_length)
        error = lib.heif_image_handle_get_metadata(handle, ids[i], p_data)
        if error.code != 0:
            raise HeifError(code=error.code, subcode=error.subcode, message=ffi.string(error.message).decode())
        data_buffer = ffi.buffer(p_data, data_length)
        data = bytes(data_buffer)
        if metadata_type=='Exif':
            # skip TIFF header, first 4 bytes
             data = data[4:]
        metadata.append({'type': metadata_type, 'data': data})

    return metadata


def _read_color_profile(handle):
    profile_type = lib.heif_image_handle_get_color_profile_type(handle)
    if profile_type == heif_color_profile_type_not_present:
        return

    color_profile = {'type': 'unknown', 'data': None}
    if profile_type == heif_color_profile_type_nclx:
        color_profile['type'] = 'nclx'
    elif profile_type == heif_color_profile_type_rICC:
        color_profile['type'] = 'rICC'
    elif profile_type == heif_color_profile_type_prof:
        color_profile['type'] = 'prof'
    data_length = lib.heif_image_handle_get_raw_color_profile_size(handle)
    p_data = ffi.new('char[]', data_length)
    error = lib.heif_image_handle_get_raw_color_profile(handle, p_data)
    if error.code != 0:
        raise HeifError(code=error.code, subcode=error.subcode, message=ffi.string(error.message).decode())
    data_buffer = ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)
    color_profile['data'] = data

    return color_profile


def _read_heif_image(img, height):
    p_stride = ffi.new('int *')
    p_data = lib.heif_image_get_plane_readonly(img, heif_channel_interleaved, p_stride);
    stride = p_stride[0]

    data_length = height * stride
    data_buffer = ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)

    return data

