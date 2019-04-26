from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("""
struct heif_context* heif_context_alloc(void);
void heif_context_free(struct heif_context*);

struct heif_error heif_context_read_from_file(
    struct heif_context*, const char* filename, const struct heif_reading_options*);
struct heif_error heif_context_read_from_memory(
    struct heif_context*, const void* mem, size_t size, const struct heif_reading_options*);

struct heif_error heif_context_get_primary_image_handle(
    struct heif_context* ctx, struct heif_image_handle**);
void heif_image_handle_release(
    const struct heif_image_handle*);

int heif_image_handle_get_width(
    const struct heif_image_handle* handle);
int heif_image_handle_get_height(
    const struct heif_image_handle* handle);
int heif_image_handle_has_alpha_channel(
    const struct heif_image_handle*);

struct heif_decoding_options
{
  uint8_t version;
  uint8_t ignore_transformations;
  void (*start_progress)(enum heif_progress_step step, int max_progress, void* progress_user_data);
  void (*on_progress)(enum heif_progress_step step, int progress, void* progress_user_data);
  void (*end_progress)(enum heif_progress_step step, void* progress_user_data);
  void* progress_user_data;
};
struct heif_decoding_options* heif_decoding_options_alloc();
void heif_decoding_options_free(struct heif_decoding_options*);

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

typedef uint32_t heif_item_id;
int heif_image_handle_get_number_of_metadata_blocks(
    const struct heif_image_handle* handle,
    const char* type_filter);
int heif_image_handle_get_list_of_metadata_block_IDs(
    const struct heif_image_handle* handle,
    const char* type_filter,
    heif_item_id* ids, int count);
const char* heif_image_handle_get_metadata_type(
    const struct heif_image_handle* handle,
    heif_item_id metadata_id);
size_t heif_image_handle_get_metadata_size(
    const struct heif_image_handle* handle,
    heif_item_id metadata_id);
struct heif_error heif_image_handle_get_metadata(
    const struct heif_image_handle* handle,
    heif_item_id metadata_id,
    void* out_data);

enum heif_color_profile_type heif_image_handle_get_color_profile_type(
    const struct heif_image_handle* handle);
size_t heif_image_handle_get_raw_color_profile_size(
    const struct heif_image_handle* handle);
struct heif_error heif_image_handle_get_raw_color_profile(
    const struct heif_image_handle* handle,
    void* out_data);

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

