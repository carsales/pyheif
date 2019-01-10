from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("""
struct heif_context* heif_context_alloc(void);
void heif_context_free(struct heif_context*);
struct heif_error heif_context_read_from_file(struct heif_context*, const char* filename, const struct heif_reading_options*);
struct heif_error heif_context_read_from_memory(struct heif_context*, const void* mem, size_t size, const struct heif_reading_options*);
struct heif_error heif_context_get_primary_image_handle(struct heif_context* ctx, struct heif_image_handle**);
void heif_image_handle_release(const struct heif_image_handle*);
int heif_image_handle_get_width(const struct heif_image_handle* handle);
int heif_image_handle_get_height(const struct heif_image_handle* handle);
int heif_image_handle_has_alpha_channel(const struct heif_image_handle*);
struct heif_error heif_decode_image(
    const struct heif_image_handle* in_handle,
    struct heif_image** out_img,
    enum heif_colorspace colorspace,
    enum heif_chroma chroma,
    const struct heif_decoding_options* options);
const uint8_t* heif_image_get_plane_readonly(
    const struct heif_image*,
    enum heif_channel channel,
    int* out_stride);
void heif_image_release(const struct heif_image*);
struct heif_error
{
  enum heif_error_code code;
  enum heif_suberror_code subcode;
  const char* message;
};
""")

ffibuilder.set_source("_libheif_cffi",
"""
     #include "libheif/heif.h"
""",
    include_dirs=['/usr/local/include'],
    library_dirs=['/usr/local/lib'],
    libraries=['heif'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)

