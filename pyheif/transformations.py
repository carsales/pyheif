class Transformations:
    """
    Represents image transformation stored in irot, imir and clap boxes.
    Unlike boxes in the file, these operations have only one proper order:
    you always should crop the image first, then rotate according to orientation_tag.
    imir and irot boxes stored in single orientation_tag. orientation_tag have
    has the same meaning as orientation tag in EXIF (values from 1 to 8)
    or could be 0 is there is no irot or imir boxes.
    In general, you may transform the image according to this tag,
    and if orientation_tag is 0, apply the value from EXIF metadata.
    """
    # EXIF orientation tag values decomposed by operations
    # 1: 0b000: NONE
    # 2: 0b001: FLIP_LEFT_RIGHT
    # 3: 0b011: ROTATE_180
    # 4: 0b010: FLIP_TOP_BOTTOM
    # 5: 0b100: TRANSPOSE
    # 6: 0b110: ROTATE_270_CCW
    # 7: 0b111: TRANSVERSE
    # 8: 0b101: ROTATE_90_CCW
    orientation_tag = 0
    crop = (0, 0, 1, 1)

    _tag_to_bitmask = [0b000, 0b000, 0b001, 0b011, 0b010, 0b100, 0b110, 0b111, 0b101]
    _bitmask_to_tag = [1, 2, 4, 3, 5, 8, 6, 7]
    _rotation_to_bitmask = [0b000, 0b101, 0b011, 0b110]

    def __init__(self, ispe_width, ispe_height):
        self.crop = (0, 0, ispe_width, ispe_height)
        self.ispe_width = ispe_width
        self.ispe_height = ispe_height

    def apply_orientation(self, *, turn_ccw=0, flip_horizontal=False, flip_vertical=False):
        """
        :param turn_ccw: number of counterclockwise turns by 90 degrees.
            0 is still image, 1 is 90 CCW, 2 it 180.
        :param flip_horizontal: flip horizontally after the turn.
        :param flip_vertical: flip vertically after the turn.
        """
        operation = self._rotation_to_bitmask[turn_ccw & 0b011]
        if flip_horizontal:
            operation ^= 0b001
        if flip_vertical:
            operation ^= 0b010

        bitmask = self._tag_to_bitmask[self.orientation_tag]
        # If bitmask contatins transposition, we swap first two bits of operation
        if bitmask & 0b100:
            bit0 = operation & 0b001
            bit1 = operation & 0b010
            operation = (operation & 0b100) | (bit0 << 1) | (bit1 >> 1)
        
        # Apply this operation
        bitmask ^= operation

        self.orientation_tag = self._bitmask_to_tag[bitmask]

    def apply_crop(self, left, top, width, height):
        bitmask = self._tag_to_bitmask[self.orientation_tag]

        if bitmask & 0b100:
            left, top = top, left
            width, height = height, width
        if bitmask & 0b001:
            left = self.ispe_width - (left + width)
        if bitmask & 0b010:
            top = self.ispe_height - (top + height)

        left = max(0, min(self.ispe_width - 1, left))
        top = max(0, min(self.ispe_height - 1, top))
        width = max(0, min(self.ispe_width - left, width))
        height = max(0, min(self.ispe_height - top, height))

        self.crop = (left, top, width, height)

    def __eq__(self, other):
        return (
            self.crop == other.crop and
            self.orientation_tag == other.orientation_tag
        )
