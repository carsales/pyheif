from _libheif_cffi import ffi


class HeifError(Exception):
    def __init__(self, *, code, subcode, message):
        self.code = code
        self.subcode = subcode
        self.message = message

    def __str__(self):
        return f'Code: {self.code}, Subcode: {self.subcode}, Message: "{self.message}"'

    def __repr__(self):
        return f'HeifError({self.code}, {self.subcode}, "{self.message}"'


class HeifNoImageError(Exception):
    def __init__(self):
        self.message = "Heif file contains no images"

    def __str__(self):
        return self.message


def _assert_success(error):
    if error.code != 0:
        raise HeifError(
            code=error.code,
            subcode=error.subcode,
            message=ffi.string(error.message).decode(),
        )
