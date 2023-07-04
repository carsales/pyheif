heif_chroma_undefined = 99
heif_chroma_monochrome = 0
heif_chroma_420 = 1
heif_chroma_422 = 2
heif_chroma_444 = 3
heif_chroma_interleaved_RGB = 10
heif_chroma_interleaved_RGBA = 11
heif_chroma_interleaved_RRGGBB_BE = 12
heif_chroma_interleaved_RRGGBBAA_BE = 13

heif_colorspace_undefined = 99
heif_colorspace_YCbCr = 0
heif_colorspace_RGB = 1
heif_colorspace_monochrome = 2

heif_channel_Y = 0
heif_channel_Cb = 1
heif_channel_Cr = 2
heif_channel_R = 3
heif_channel_G = 4
heif_channel_B = 5
heif_channel_Alpha = 6
heif_channel_interleaved = 10


def encode_fourcc(fourcc):
    encoded = (
        ord(fourcc[0]) << 24
        | ord(fourcc[1]) << 16
        | ord(fourcc[2]) << 8
        | ord(fourcc[3])
    )
    return encoded


heif_color_profile_type_not_present = 0
heif_color_profile_type_nclx = encode_fourcc("nclx")
heif_color_profile_type_rICC = encode_fourcc("rICC")
heif_color_profile_type_prof = encode_fourcc("prof")

heif_filetype_no = 0
heif_filetype_yes_supported = 1
heif_filetype_yes_unsupported = 2
heif_filetype_maybe = 3

heif_item_property_type_user_description = encode_fourcc("udes")
heif_item_property_type_transform_mirror = encode_fourcc("imir")
heif_item_property_type_transform_rotation = encode_fourcc("irot")
heif_item_property_type_transform_crop = encode_fourcc("clap")
heif_item_property_type_image_size = encode_fourcc("ispe")

heif_transform_mirror_direction_vertical = 0
heif_transform_mirror_direction_horizontal = 1

LIBHEIF_AUX_IMAGE_FILTER_OMIT_ALPHA = 0x2
LIBHEIF_AUX_IMAGE_FILTER_OMIT_DEPTH = 0x4
