struct heif_context;
struct heif_image_handle;
struct heif_image;
struct heif_reading_options;

struct heif_error
{
  // main error category
  enum heif_error_code code;

  // more detailed error code
  enum heif_suberror_code subcode;

  // textual error message (is always defined, you do not have to check for NULL)
  const char* message;
};

typedef uint32_t heif_item_id;
typedef uint32_t heif_property_id;

enum heif_chroma
{
  heif_chroma_undefined = 99,
  heif_chroma_monochrome = 0,
  heif_chroma_420 = 1,
  heif_chroma_422 = 2,
  heif_chroma_444 = 3,
  heif_chroma_interleaved_RGB = 10,
  heif_chroma_interleaved_RGBA = 11,
  heif_chroma_interleaved_RRGGBB_BE = 12,   // HDR, big endian.
  heif_chroma_interleaved_RRGGBBAA_BE = 13, // HDR, big endian.
  heif_chroma_interleaved_RRGGBB_LE = 14,   // HDR, little endian.
  heif_chroma_interleaved_RRGGBBAA_LE = 15  // HDR, little endian.
};

enum heif_colorspace
{
  heif_colorspace_undefined = 99,

  // heif_colorspace_YCbCr should be used with one of these heif_chroma values:
  // * heif_chroma_444
  // * heif_chroma_422
  // * heif_chroma_420
  heif_colorspace_YCbCr = 0,

  // heif_colorspace_RGB should be used with one of these heif_chroma values:
  // * heif_chroma_444 (for planar RGB)
  // * heif_chroma_interleaved_RGB
  // * heif_chroma_interleaved_RGBA
  // * heif_chroma_interleaved_RRGGBB_BE
  // * heif_chroma_interleaved_RRGGBBAA_BE
  // * heif_chroma_interleaved_RRGGBB_LE
  // * heif_chroma_interleaved_RRGGBBAA_LE
  heif_colorspace_RGB = 1,

  // heif_colorspace_monochrome should only be used with heif_chroma = heif_chroma_monochrome
  heif_colorspace_monochrome = 2
};

enum heif_channel
{
  heif_channel_Y = 0,
  heif_channel_Cb = 1,
  heif_channel_Cr = 2,
  heif_channel_R = 3,
  heif_channel_G = 4,
  heif_channel_B = 5,
  heif_channel_Alpha = 6,
  heif_channel_interleaved = 10
};


// Version string of linked libheif library.
const char* heif_get_version(void);

enum heif_filetype_result
{
  heif_filetype_no,
  heif_filetype_yes_supported,   // it is heif and can be read by libheif
  heif_filetype_yes_unsupported, // it is heif, but cannot be read by libheif
  heif_filetype_maybe // not sure whether it is an heif, try detection with more input data
};

// input data should be at least 12 bytes
enum heif_filetype_result heif_check_filetype(const uint8_t* data, int len);

// Allocate a new context for reading HEIF files.
// Has to be freed again with heif_context_free().
struct heif_context* heif_context_alloc(void);

// Free a previously allocated HEIF context. You should not free a context twice.
void heif_context_free(struct heif_context*);

// Same as heif_context_read_from_memory() except that the provided memory is not copied.
// That means, you will have to keep the memory area alive as long as you use the heif_context.
struct heif_error heif_context_read_from_memory_without_copy(struct heif_context*,
                                                             const void* mem, size_t size,
                                                             const struct heif_reading_options*);

// Number of top-level images in the HEIF file. This does not include the thumbnails or the
// tile images that are composed to an image grid. You can get access to the thumbnails via
// the main image handle.
int heif_context_get_number_of_top_level_images(struct heif_context* ctx);

// Fills in image IDs into the user-supplied int-array 'ID_array', preallocated with 'count' entries.
// Function returns the total number of IDs filled into the array.
int heif_context_get_list_of_top_level_image_IDs(struct heif_context* ctx,
                                                 heif_item_id* ID_array,
                                                 int count);

struct heif_error heif_context_get_primary_image_ID(struct heif_context* ctx, heif_item_id* id);

// Get the image handle for a known image ID.
struct heif_error heif_context_get_image_handle(struct heif_context* ctx,
                                                heif_item_id id,
                                                struct heif_image_handle**);

// ========================= heif_image_handle =========================

// An heif_image_handle is a handle to a logical image in the HEIF file.
// To get the actual pixel data, you have to decode the handle to an heif_image.
// An heif_image_handle also gives you access to the thumbnails and Exif data
// associated with an image.

// Once you obtained an heif_image_handle, you can already release the heif_context,
// since it is internally ref-counted.

// Release image handle.
void heif_image_handle_release(const struct heif_image_handle*);

heif_item_id heif_image_handle_get_item_id(const struct heif_image_handle* handle);

// Get the resolution of an image.
int heif_image_handle_get_width(const struct heif_image_handle* handle);

int heif_image_handle_get_height(const struct heif_image_handle* handle);

int heif_image_handle_has_alpha_channel(const struct heif_image_handle*);

// Get the image width from the 'ispe' box. This is the original image size without
// any transformations applied to it. Do not use this unless you know exactly what
// you are doing.
int heif_image_handle_get_ispe_width(const struct heif_image_handle* handle);

int heif_image_handle_get_ispe_height(const struct heif_image_handle* handle);

// Returns -1 on error, e.g. if this information is not present in the image.
int heif_image_handle_get_luma_bits_per_pixel(const struct heif_image_handle*);


// ------------------------- item properties -------------------------

enum heif_item_property_type
{
//  heif_item_property_unknown = -1,
  heif_item_property_type_invalid = 0,
};

// Returns all transformative properties in the correct order.
// This includes "irot", "imir", "clap".
// The number of properties is returned, which are not more than 'count' if (out_list != nullptr).
// By setting out_list==nullptr, you can query the number of properties, 'count' is ignored.
int heif_item_get_transformation_properties(const struct heif_context* context,
                                            heif_item_id id,
                                            heif_property_id* out_list,
                                            int count);

enum heif_item_property_type heif_item_get_property_type(const struct heif_context* context,
                                                         heif_item_id id,
                                                         heif_property_id property_id);

enum heif_transform_mirror_direction
{
  heif_transform_mirror_direction_vertical = 0,    // flip image vertically
  heif_transform_mirror_direction_horizontal = 1   // flip image horizontally
};

// Will return 'heif_transform_mirror_direction_invalid' in case of error.
enum heif_transform_mirror_direction heif_item_get_property_transform_mirror(const struct heif_context* context,
                                                                             heif_item_id itemId,
                                                                             heif_property_id propertyId);

// Returns only 0, 90, 180, or 270 angle values.
// Returns -1 in case of error (but it will only return an error in case of wrong usage).
int heif_item_get_property_transform_rotation_ccw(const struct heif_context* context,
                                                  heif_item_id itemId,
                                                  heif_property_id propertyId);

// Returns the number of pixels that should be removed from the four edges.
// Because of the way this data is stored, you have to pass the image size at the moment of the crop operation
// to compute the cropped border sizes.
void heif_item_get_property_transform_crop_borders(const struct heif_context* context,
                                                   heif_item_id itemId,
                                                   heif_property_id propertyId,
                                                   int image_width, int image_height,
                                                   int* left, int* top, int* right, int* bottom);

// ------------------------- depth images -------------------------

int heif_image_handle_has_depth_image(const struct heif_image_handle*);

int heif_image_handle_get_list_of_depth_image_IDs(const struct heif_image_handle* handle,
                                                  heif_item_id* ids, int count);

struct heif_error heif_image_handle_get_depth_image_handle(const struct heif_image_handle* handle,
                                                           heif_item_id depth_image_id,
                                                           struct heif_image_handle** out_depth_handle);

// ------------------------- auxiliary images -------------------------

// List the number of auxiliary images assigned to this image handle.
int heif_image_handle_get_number_of_auxiliary_images(const struct heif_image_handle* handle,
                                                     int aux_filter);

int heif_image_handle_get_list_of_auxiliary_image_IDs(const struct heif_image_handle* handle,
                                                      int aux_filter,
                                                      heif_item_id* ids, int count);

// You are responsible to deallocate the returned buffer with heif_image_handle_release_auxiliary_type().
struct heif_error heif_image_handle_get_auxiliary_type(const struct heif_image_handle* handle,
                                                       const char** out_type);

void heif_image_handle_release_auxiliary_type(const struct heif_image_handle* handle,
                                              const char** out_type);

// Get the image handle of an auxiliary image.
struct heif_error heif_image_handle_get_auxiliary_image_handle(const struct heif_image_handle* main_image_handle,
                                                               heif_item_id auxiliary_id,
                                                               struct heif_image_handle** out_auxiliary_handle);


// ------------------------- metadata (Exif / XMP) -------------------------

// How many metadata blocks are attached to an image. If you only want to get EXIF data,
// set the type_filter to "Exif". Otherwise, set the type_filter to NULL.
int heif_image_handle_get_number_of_metadata_blocks(const struct heif_image_handle* handle,
                                                    const char* type_filter);

// 'type_filter' can be used to get only metadata of specific types, like "Exif".
// If 'type_filter' is NULL, it will return all types of metadata IDs.
int heif_image_handle_get_list_of_metadata_block_IDs(const struct heif_image_handle* handle,
                                                     const char* type_filter,
                                                     heif_item_id* ids, int count);

// Return a string indicating the type of the metadata, as specified in the HEIF file.
// Exif data will have the type string "Exif".
// This string will be valid until the next call to a libheif function.
// You do not have to free this string.
const char* heif_image_handle_get_metadata_type(const struct heif_image_handle* handle,
                                                heif_item_id metadata_id);

// Get the size of the raw metadata, as stored in the HEIF file.
size_t heif_image_handle_get_metadata_size(const struct heif_image_handle* handle,
                                           heif_item_id metadata_id);

// 'out_data' must point to a memory area of the size reported by heif_image_handle_get_metadata_size().
// The data is returned exactly as stored in the HEIF file.
// For Exif data, you probably have to skip the first four bytes of the data, since they
// indicate the offset to the start of the TIFF header of the Exif data.
struct heif_error heif_image_handle_get_metadata(const struct heif_image_handle* handle,
                                                 heif_item_id metadata_id,
                                                 void* out_data);

// ------------------------- color profiles -------------------------

enum heif_color_profile_type
{
  heif_color_profile_type_not_present = 0,
};


// Returns 'heif_color_profile_type_not_present' if there is no color profile.
// If there is an ICC profile and an NCLX profile, the ICC profile is returned.
enum heif_color_profile_type heif_image_handle_get_color_profile_type(const struct heif_image_handle* handle);

size_t heif_image_handle_get_raw_color_profile_size(const struct heif_image_handle* handle);

// Returns 'heif_error_Color_profile_does_not_exist' when there is no ICC profile.
struct heif_error heif_image_handle_get_raw_color_profile(const struct heif_image_handle* handle,
                                                          void* out_data);

struct heif_color_profile_nclx
{
  // === version 1 fields

  uint8_t version;

  enum heif_color_primaries color_primaries;
  enum heif_transfer_characteristics transfer_characteristics;
  enum heif_matrix_coefficients matrix_coefficients;
  uint8_t full_range_flag;

  // --- decoded values (not used when saving nclx)

  float color_primary_red_x, color_primary_red_y;
  float color_primary_green_x, color_primary_green_y;
  float color_primary_blue_x, color_primary_blue_y;
  float color_primary_white_x, color_primary_white_y;
};

// Returns 'heif_error_Color_profile_does_not_exist' when there is no NCLX profile.
// TODO: This function does currently not return an NCLX profile if it is stored in the image bitstream.
//       Only NCLX profiles stored as colr boxes are returned. This may change in the future.
struct heif_error heif_image_handle_get_nclx_color_profile(const struct heif_image_handle* handle,
                                                           struct heif_color_profile_nclx** out_data);

void heif_nclx_color_profile_free(struct heif_color_profile_nclx* nclx_profile);

// ========================= heif_image =========================

// An heif_image contains a decoded pixel image in various colorspaces, chroma formats,
// and bit depths.

// Note: when converting images to an interleaved chroma format, the resulting
// image contains only a single channel of type channel_interleaved with, e.g., 3 bytes per pixel,
// containing the interleaved R,G,B values.

// Planar RGB images are specified as heif_colorspace_RGB / heif_chroma_444.

enum heif_progress_step
{
  heif_progress_step_total = 0,
  heif_progress_step_load_tile = 1
};


enum heif_chroma_downsampling_algorithm
{
  heif_chroma_downsampling_nearest_neighbor = 1,
  heif_chroma_downsampling_average = 2,

  // Combine with 'heif_chroma_upsampling_bilinear' for best quality.
  // Makes edges look sharper when using YUV 420 with bilinear chroma upsampling.
  heif_chroma_downsampling_sharp_yuv = 3
};

enum heif_chroma_upsampling_algorithm
{
  heif_chroma_upsampling_nearest_neighbor = 1,
  heif_chroma_upsampling_bilinear = 2
};

struct heif_color_conversion_options
{
  uint8_t version;

  // --- version 1 options

  enum heif_chroma_downsampling_algorithm preferred_chroma_downsampling_algorithm;
  enum heif_chroma_upsampling_algorithm preferred_chroma_upsampling_algorithm;

  // When set to 'false' libheif may also use a different algorithm if the preferred one is not available
  // or using a different algorithm is computationally less complex. Note that currently (v1.17.0) this
  // means that for RGB input it will usually choose nearest-neighbor sampling because this is computationally
  // the simplest.
  // Set this field to 'true' if you want to make sure that the specified algorithm is used even
  // at the cost of slightly higher computation times.
  uint8_t only_use_preferred_chroma_algorithm;
};


struct heif_decoding_options
{
  uint8_t version;

  // version 1 options

  // Ignore geometric transformations like cropping, rotation, mirroring.
  // Default: false (do not ignore).
  uint8_t ignore_transformations;

  void (* start_progress)(enum heif_progress_step step, int max_progress, void* progress_user_data);

  void (* on_progress)(enum heif_progress_step step, int progress, void* progress_user_data);

  void (* end_progress)(enum heif_progress_step step, void* progress_user_data);

  void* progress_user_data;

  // version 2 options

  uint8_t convert_hdr_to_8bit;

  // version 3 options

  // When enabled, an error is returned for invalid input. Otherwise, it will try its best and
  // add decoding warnings to the decoded heif_image. Default is non-strict.
  uint8_t strict_decoding;

  // version 4 options

  // name_id of the decoder to use for the decoding.
  // If set to NULL (default), the highest priority decoder is chosen.
  // The priority is defined in the plugin.
  const char* decoder_id;


  // version 5 options

  struct heif_color_conversion_options color_conversion_options;
};


// Allocate decoding options and fill with default values.
// Note: you should always get the decoding options through this function since the
// option structure may grow in size in future versions.
struct heif_decoding_options* heif_decoding_options_alloc(void);

void heif_decoding_options_free(struct heif_decoding_options*);

// Decode an heif_image_handle into the actual pixel image and also carry out
// all geometric transformations specified in the HEIF file (rotation, cropping, mirroring).
//
// If colorspace or chroma is set to heif_colorspace_undefined or heif_chroma_undefined,
// respectively, the original colorspace is taken.
// Decoding options may be NULL. If you want to supply options, always use
// heif_decoding_options_alloc() to get the structure.
struct heif_error heif_decode_image(const struct heif_image_handle* in_handle,
                                    struct heif_image** out_img,
                                    enum heif_colorspace colorspace,
                                    enum heif_chroma chroma,
                                    const struct heif_decoding_options* options);

// Get a pointer to the actual pixel data.
// The 'out_stride' is returned as "bytes per line".
// When out_stride is NULL, no value will be written.
// Returns NULL if a non-existing channel was given.
const uint8_t* heif_image_get_plane_readonly(const struct heif_image*,
                                             enum heif_channel channel,
                                             int* out_stride);

// Release heif_image.
void heif_image_release(const struct heif_image*);
