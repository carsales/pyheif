import os

from cffi import FFI

ffibuilder = FFI()

with open("libheif/heif.h") as f:
    ffibuilder.cdef(f.read())

include_dirs = ["/usr/local/include", "/usr/include", "/opt/local/include"]
library_dirs = ["/usr/local/lib", "/usr/lib", "/lib", "/opt/local/lib"]

homebrew_path = os.getenv('HOMEBREW_PREFIX')
if homebrew_path:
    include_dirs.append(os.path.join(homebrew_path, "include"))
    library_dirs.append(os.path.join(homebrew_path, "lib"))

ffibuilder.set_source(
    "_libheif_cffi",
    """
     #include "libheif/heif.h"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["heif"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)