heif_chroma_undefined=99
heif_chroma_monochrome=0
heif_chroma_420=1
heif_chroma_422=2
heif_chroma_444=3
heif_chroma_interleaved_RGB=10
heif_chroma_interleaved_RGBA=11

heif_colorspace_undefined=99
heif_colorspace_YCbCr=0
heif_colorspace_RGB=1
heif_colorspace_monochrome=2

heif_channel_Y = 0
heif_channel_Cb = 1
heif_channel_Cr = 2
heif_channel_R = 3
heif_channel_G = 4
heif_channel_B = 5
heif_channel_Alpha = 6
heif_channel_interleaved = 10

def encode_fourcc(fourcc):
    encoded = ord(fourcc[0])<<24 | ord(fourcc[1])<<16 | ord(fourcc[2])<<8 | ord(fourcc[3])
    return encoded
heif_color_profile_type_not_present = 0
heif_color_profile_type_nclx = encode_fourcc('nclx')
heif_color_profile_type_rICC = encode_fourcc('rICCC')
heif_color_profile_type_prof = encode_fourcc('prof')

