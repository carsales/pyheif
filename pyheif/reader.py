import builtins
import functools
import pathlib
import warnings

from _libheif_cffi import ffi, lib as libheif
from . import constants as _constants
from .error import _assert_success, HeifNoImageError


class HeifImage:
    def __init__(
        self, *, size, has_alpha, bit_depth, metadata, color_profile, data, stride
    ):
        self.size = size
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.metadata = metadata
        self.color_profile = color_profile
        self.data = data
        self.stride = stride

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {str(len(self.data)) + ' bytes' if self.data else 'no'} data>"
        )

    def load(self):
        return self  # already loaded

    def close(self):
        pass  # TODO: release self.data here?


class UndecodedHeifImage(HeifImage):
    def __init__(
        self, heif_handle, *, apply_transformations, convert_hdr_to_8bit, **kwargs
    ):
        self._heif_handle = heif_handle
        self.apply_transformations = apply_transformations
        self.convert_hdr_to_8bit = convert_hdr_to_8bit
        super().__init__(data=None, stride=None, **kwargs)

    def load(self):
        self.data, self.stride = _read_heif_image(self._heif_handle, self)
        self.close()
        self.__class__ = HeifImage
        return self

    def close(self):
        # Don't call super().close() here, we don't need to free bytes.
        if hasattr(self, "_heif_handle"):
            del self._heif_handle


# This names are deprecated an will be removed in 1.0
HeifFile = HeifImage
UndecodedHeifFile = UndecodedHeifImage


class HeifContainer:
    def __init__(self, primary_image, top_level_images):
        self.primary_image = primary_image
        self.top_level_images = top_level_images


class HeifTopLevelImage:
    def __init__(self, id, image, is_primary, depth_image, auxiliary_images):
        self.id = id
        self.image = image
        self.is_primary = is_primary
        self.depth_image = depth_image
        self.auxiliary_images = auxiliary_images


class HeifDepthImage:
    def __init__(self, id, image):
        self.id = id
        self.image = image


class HeifAuxiliaryImage:
    def __init__(self, id, type, image):
        self.id = id
        self.type = type
        self.image = image


def check(fp):
    magic = _get_bytes(fp, 12)
    filetype_check = libheif.heif_check_filetype(magic, len(magic))
    return filetype_check


def read_heif(fp, apply_transformations=True):
    warnings.warn("read_heif is deprecated, use read() instead", DeprecationWarning)
    return read(fp, apply_transformations=apply_transformations)


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    heif_file = open(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file.load()


def open(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    heif_container = open_container(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_container.primary_image.image


def open_container(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    d = _get_bytes(fp)
    ctx = _get_heif_context(d)
    return _read_heif_container(ctx, apply_transformations, convert_hdr_to_8bit)


def _get_bytes(fp, length=None):
    if isinstance(fp, (str, pathlib.Path)):
        with builtins.open(fp, "rb") as f:
            d = f.read(length or -1)
    elif hasattr(fp, "read"):
        d = fp.read(length or -1)
    else:
        d = bytes(fp)[:length]

    return d


def _keep_refs(destructor, **refs):
    """
    Keep refs to passed arguments until `inner` callback exist.
    This prevents collecting parent objects until all children collected.
    """

    def inner(cdata):
        return destructor(cdata)

    inner._refs = refs
    return inner


def _get_heif_context(d):
    magic = d[:12]
    filetype_check = libheif.heif_check_filetype(magic, len(magic))
    if filetype_check == _constants.heif_filetype_no:
        raise ValueError("Input is not a HEIF/AVIF file")
    elif filetype_check == _constants.heif_filetype_yes_unsupported:
        warnings.warn("Input is an unsupported HEIF/AVIF file type - trying anyway!")

    ctx = libheif.heif_context_alloc()
    collect = _keep_refs(libheif.heif_context_free, data=d)
    ctx = ffi.gc(ctx, collect, size=len(d))

    error = libheif.heif_context_read_from_memory_without_copy(ctx, d, len(d), ffi.NULL)
    _assert_success(error)
    return ctx


def _read_heif_container(ctx, apply_transformations, convert_hdr_to_8bit):
    image_count = libheif.heif_context_get_number_of_top_level_images(ctx)
    if image_count == 0:
        raise HeifNoImageError()

    ids = ffi.new("heif_item_id[]", image_count)
    image_count = libheif.heif_context_get_list_of_top_level_image_IDs(
        ctx, ids, image_count
    )

    p_primary_image_id = ffi.new("heif_item_id *")
    error = libheif.heif_context_get_primary_image_ID(ctx, p_primary_image_id)
    _assert_success(error)
    primary_image_id = p_primary_image_id[0]
    primary_image = None
    top_level_images = []

    for handle_id in ids:
        p_handle = ffi.new("struct heif_image_handle **")
        error = libheif.heif_context_get_image_handle(ctx, handle_id, p_handle)
        _assert_success(error)

        collect = _keep_refs(libheif.heif_image_handle_release, ctx=ctx)
        handle = ffi.gc(p_handle[0], collect)

        image = _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit)

        is_primary = handle_id == primary_image_id

        depth_image = _read_depth_image(
            handle, apply_transformations, convert_hdr_to_8bit
        )
        auxiliary_images = _read_all_auxiliary_images(
            handle, apply_transformations, convert_hdr_to_8bit
        )

        top_level_image = HeifTopLevelImage(
            handle_id, image, is_primary, depth_image, auxiliary_images
        )

        top_level_images.append(top_level_image)
        if is_primary:
            primary_image = top_level_image

    return HeifContainer(primary_image, top_level_images)


def _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit):
    width = libheif.heif_image_handle_get_width(handle)
    height = libheif.heif_image_handle_get_height(handle)
    has_alpha = bool(libheif.heif_image_handle_has_alpha_channel(handle))
    bit_depth = libheif.heif_image_handle_get_luma_bits_per_pixel(handle)

    metadata = _read_metadata(handle)
    color_profile = _read_color_profile(handle)

    heif_file = UndecodedHeifImage(
        handle,
        size=(width, height),
        has_alpha=has_alpha,
        bit_depth=bit_depth,
        metadata=metadata,
        color_profile=color_profile,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file


def _read_depth_image(handle, apply_transformations, convert_hdr_to_8bit):
    has_depth_image = libheif.heif_image_handle_has_depth_image(handle)
    if has_depth_image:
        p_depth_image_id = ffi.new("heif_item_id *")
        n_depth_images = libheif.heif_image_handle_get_list_of_depth_image_IDs(
            handle, p_depth_image_id, 1
        )
        if n_depth_images == 1:
            depth_id = p_depth_image_id[0]
            p_depth_handle = ffi.new("struct heif_image_handle **")
            error = libheif.heif_image_handle_get_depth_image_handle(
                handle, depth_id, p_depth_handle
            )
            _assert_success(error)
            collect = _keep_refs(libheif.heif_image_handle_release, handle=handle)
            depth_handle = ffi.gc(p_depth_handle[0], collect)
            return HeifDepthImage(
                depth_id,
                _read_heif_handle(
                    depth_handle, apply_transformations, convert_hdr_to_8bit
                ),
            )
    return None


def _read_all_auxiliary_images(handle, apply_transformations, convert_hdr_to_8bit):
    aux_count = libheif.heif_image_handle_get_number_of_auxiliary_images(
        handle,
        _constants.LIBHEIF_AUX_IMAGE_FILTER_OMIT_ALPHA
        | _constants.LIBHEIF_AUX_IMAGE_FILTER_OMIT_DEPTH,
    )
    if aux_count == 0:
        return []
    aux_ids = ffi.new("heif_item_id[]", aux_count)
    aux_count = libheif.heif_image_handle_get_list_of_auxiliary_image_IDs(
        handle,
        _constants.LIBHEIF_AUX_IMAGE_FILTER_OMIT_ALPHA
        | _constants.LIBHEIF_AUX_IMAGE_FILTER_OMIT_DEPTH,
        aux_ids,
        aux_count,
    )
    auxiliaries = []
    for aux_id in aux_ids:
        aux_image = _read_auxiliary_image(
            handle, aux_id, apply_transformations, convert_hdr_to_8bit
        )
        auxiliaries.append(aux_image)
    return auxiliaries


def _read_auxiliary_image(
    handle, auxiliary_image_id, apply_transformations, convert_hdr_to_8bit
):
    p_aux_handle = ffi.new("struct heif_image_handle **")
    error = libheif.heif_image_handle_get_auxiliary_image_handle(
        handle, auxiliary_image_id, p_aux_handle
    )
    _assert_success(error)

    collect = _keep_refs(libheif.heif_image_handle_release, handle=handle)
    aux_handle = ffi.gc(p_aux_handle[0], collect)

    p_aux_type = ffi.new("char **")
    error = libheif.heif_image_handle_get_auxiliary_type(aux_handle, p_aux_type)
    _assert_success(error)
    aux_type = ffi.string(p_aux_type[0]).decode()
    libheif.heif_image_handle_free_auxiliary_types(aux_handle, p_aux_type)

    return HeifAuxiliaryImage(
        auxiliary_image_id,
        aux_type,
        _read_heif_handle(aux_handle, apply_transformations, convert_hdr_to_8bit),
    )


def _read_metadata(handle):
    block_count = libheif.heif_image_handle_get_number_of_metadata_blocks(
        handle, ffi.NULL
    )
    if block_count == 0:
        return

    metadata = []
    ids = ffi.new("heif_item_id[]", block_count)
    libheif.heif_image_handle_get_list_of_metadata_block_IDs(
        handle, ffi.NULL, ids, block_count
    )
    for i in range(len(ids)):
        metadata_type = libheif.heif_image_handle_get_metadata_type(handle, ids[i])
        metadata_type = ffi.string(metadata_type).decode()
        data_length = libheif.heif_image_handle_get_metadata_size(handle, ids[i])
        p_data = ffi.new("char[]", data_length)
        error = libheif.heif_image_handle_get_metadata(handle, ids[i], p_data)
        _assert_success(error)

        data_buffer = ffi.buffer(p_data, data_length)
        data = bytes(data_buffer)
        if metadata_type == "Exif":
            # skip TIFF header, first 4 bytes
            data = data[4:]
        metadata.append({"type": metadata_type, "data": data})

    return metadata


def _read_color_profile(handle):
    profile_type = libheif.heif_image_handle_get_color_profile_type(handle)
    if profile_type == _constants.heif_color_profile_type_not_present:
        return

    color_profile = {"type": "unknown", "data": None}
    if profile_type == _constants.heif_color_profile_type_nclx:
        color_profile["type"] = "nclx"
        data_length = ffi.sizeof("struct heif_color_profile_nclx")
        pp_data = ffi.new("struct heif_color_profile_nclx * *")
        error = libheif.heif_image_handle_get_nclx_color_profile(handle, pp_data)
        p_data = ffi.gc(pp_data[0], libheif.heif_nclx_color_profile_free)

    else:
        if profile_type == _constants.heif_color_profile_type_rICC:
            color_profile["type"] = "rICC"
        elif profile_type == _constants.heif_color_profile_type_prof:
            color_profile["type"] = "prof"
        data_length = libheif.heif_image_handle_get_raw_color_profile_size(handle)
        p_data = ffi.new("char[]", data_length)
        error = libheif.heif_image_handle_get_raw_color_profile(handle, p_data)

    _assert_success(error)
    data_buffer = ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)
    color_profile["data"] = data

    return color_profile


def _read_heif_image(handle, heif_file):
    colorspace = _constants.heif_colorspace_RGB
    if heif_file.convert_hdr_to_8bit or heif_file.bit_depth <= 8:
        if heif_file.has_alpha:
            chroma = _constants.heif_chroma_interleaved_RGBA
        else:
            chroma = _constants.heif_chroma_interleaved_RGB
    else:
        if heif_file.has_alpha:
            chroma = _constants.heif_chroma_interleaved_RRGGBBAA_BE
        else:
            chroma = _constants.heif_chroma_interleaved_RRGGBB_BE

    p_options = libheif.heif_decoding_options_alloc()
    p_options = ffi.gc(p_options, libheif.heif_decoding_options_free)
    p_options.ignore_transformations = int(not heif_file.apply_transformations)
    p_options.convert_hdr_to_8bit = int(heif_file.convert_hdr_to_8bit)

    p_img = ffi.new("struct heif_image **")
    error = libheif.heif_decode_image(
        handle, p_img, colorspace, chroma, p_options,
    )
    _assert_success(error)

    img = p_img[0]

    p_stride = ffi.new("int *")
    p_data = libheif.heif_image_get_plane_readonly(
        img, _constants.heif_channel_interleaved, p_stride
    )
    stride = p_stride[0]

    data_length = heif_file.size[1] * stride

    # Release image as soon as no references to p_data left
    collect = functools.partial(_release_heif_image, img)
    p_data = ffi.gc(p_data, collect, size=data_length)

    # ffi.buffer obligatory keeps a reference to p_data
    data_buffer = ffi.buffer(p_data, data_length)

    return data_buffer, stride


def _release_heif_image(img, p_data=None):
    libheif.heif_image_release(img)
