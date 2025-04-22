# -*- coding: utf-8 -*-
"""A small Python module for BMP image processing.

- Author: Quan Lin
- License: MIT
"""

from struct import pack, unpack

# Project Version
__version__ = "0.1.0"
__all__ = ["MicroBMP"]


class MicroBMP(object):
    def __init__(self, width=None, height=None, depth=None, palette=None):
        # BMP Header
        self.BMP_id = b"BM"
        self.BMP_size = None
        self.BMP_reserved1 = b"\x00\x00"
        self.BMP_reserved2 = b"\x00\x00"
        self.BMP_offset = None

        # DIB Header
        self.DIB_len = 40
        self.DIB_w = width
        self.DIB_h = height
        self.DIB_planes_num = 1
        self.DIB_depth = depth
        self.DIB_comp = 0
        self.DIB_raw_size = None
        self.DIB_hres = 2835  # 72 DPI * 39.3701 inches/metre.
        self.DIB_vres = 2835
        self.DIB_num_in_plt = None
        self.DIB_extra = None

        self.palette = palette
        self.parray = None  # Pixel array

        self.ppb = None  # Number of pixels per byte for depth <= 8.
        self.pmask = None  # Pixel Mask
        self.row_size = None
        self.padded_row_size = None

        self.initialised = False
        self._init()

    def __getitem__(self, key):
        assert self.initialised, "Image not initialised!"
        assert key[0] < self.DIB_w and key[1] < self.DIB_h, "Out of image boundary!"

        # Pixels are arranged in HLSB format with high bits being the leftmost
        pindex = key[1] * self.DIB_w + key[0]  # Pixel index
        if self.DIB_depth <= 8:
            return self._extract_from_bytes(self.parray, pindex)
        else:
            pindex *= 3
            if (len(key) > 2) and (key[2] in (0, 1, 2)):
                return self.parray[pindex + key[2]]
            else:
                return (
                    self.parray[pindex],
                    self.parray[pindex + 1],
                    self.parray[pindex + 2],
                )

    def __setitem__(self, key, value):
        assert self.initialised, "Image not initialised!"
        assert key[0] < self.DIB_w and key[1] < self.DIB_h, "Out of image boundary!"

        # Pixels are arranged in HLSB format with high bits being the leftmost
        pindex = key[1] * self.DIB_w + key[0]  # Pixel index
        if self.DIB_depth <= 8:
            self._fill_in_bytes(self.parray, pindex, value)
        else:
            pindex *= 3
            if (len(key) > 2) and (key[2] in (0, 1, 2)):
                self.parray[pindex + key[2]] = value
            else:
                self.parray[pindex] = value[0]
                self.parray[pindex + 1] = value[1]
                self.parray[pindex + 2] = value[2]

    def __str__(self):
        if not self.initialised:
            return repr(self)

        return "BMP image, {}, {}-bit, {}x{} pixels, {} bytes".format(
            "indexed" if self.DIB_depth <= 8 else "RGB",
            self.DIB_depth,
            self.DIB_w,
            self.DIB_h,
            self.BMP_size,
        )

    def _init(self):
        if None in (self.DIB_w, self.DIB_h, self.DIB_depth):
            self.initialised = False
            return self.initialised

        assert self.BMP_id == b"BM", "BMP id ({}) must be b'BM'!".format(self.BMP_id)
        assert (
            len(self.BMP_reserved1) == 2 and len(self.BMP_reserved2) == 2
        ), "Length of BMP reserved fields ({}+{}) must be 2+2!".format(
            len(self.BMP_reserved1), len(self.BMP_reserved2)
        )
        assert self.DIB_planes_num == 1, "DIB planes number ({}) must be 1!".format(
            self.DIB_planes_num
        )
        assert self.DIB_depth in (
            1,
            2,
            4,
            8,
            24,
        ), "Colour depth ({}) must be in (1, 2, 4, 8, 24)!".format(self.DIB_depth)
        assert (
            self.DIB_comp == 0
            or (self.DIB_depth == 8 and self.DIB_comp == 1)
            or (self.DIB_depth == 4 and self.DIB_comp == 2)
        ), "Colour depth + compression ({}+{}) must be X+0/8+1/4+2!".format(
            self.DIB_depth, self.DIB_comp
        )

        if self.DIB_depth <= 8:
            self.ppb = 8 // self.DIB_depth
            self.pmask = 0xFF >> (8 - self.DIB_depth)
            if self.palette is None:
                # Default palette is black and white or full size grey scale.
                self.DIB_num_in_plt = 2 ** self.DIB_depth
                self.palette = [None for i in range(self.DIB_num_in_plt)]
                for i in range(self.DIB_num_in_plt):
                    # Assignment that suits all: 1/2/4/8-bit colour depth.
                    s = 255 * i // (self.DIB_num_in_plt - 1)
                    self.palette[i] = bytearray([s, s, s])
            else:
                self.DIB_num_in_plt = len(self.palette)
        else:
            self.ppb = None
            self.pmask = None
            self.DIB_num_in_plt = 0
            self.palette = None

        if self.parray is None:
            if self.DIB_depth <= 8:
                div, mod = divmod(self.DIB_w * self.DIB_h, self.ppb)
                self.parray = bytearray(div + (1 if mod else 0))
            else:
                self.parray = bytearray(self.DIB_w * self.DIB_h * 3)

        plt_size = self.DIB_num_in_plt * 4
        self.BMP_offset = 14 + self.DIB_len + plt_size
        self.row_size = self._size_from_width(self.DIB_w)
        self.padded_row_size = self._padded_size_from_size(self.row_size)
        if self.DIB_comp == 0:
            self.DIB_raw_size = self.padded_row_size * self.DIB_h
            self.BMP_size = self.BMP_offset + self.DIB_raw_size

        self.initialised = True
        return self.initialised

    def _size_from_width(self, width):
        return (width * self.DIB_depth + 7) // 8

    def _padded_size_from_size(self, size):
        return (size + 3) // 4 * 4

    def _extract_from_bytes(self, data, index):
        # One formula that suits all: 1/2/4/8-bit colour depth.
        byte_index, pos_in_byte = divmod(index, self.ppb)
        shift = 8 - self.DIB_depth * (pos_in_byte + 1)
        return (data[byte_index] >> shift) & self.pmask

    def _fill_in_bytes(self, data, index, value):
        # One formula that suits all: 1/2/4/8-bit colour depth.
        byte_index, pos_in_byte = divmod(index, self.ppb)
        shift = 8 - self.DIB_depth * (pos_in_byte + 1)
        value &= self.pmask
        data[byte_index] = (data[byte_index] & ~(self.pmask << shift)) + (
            value << shift
        )

    def _decode_rle(self, bf_io):
        # Only bottom-up bitmap can be compressed.
        x, y = 0, self.DIB_h - 1
        while True:
            data = bf_io.read(2)
            if data[0] == 0:
                if data[1] == 0:
                    x, y = 0, y - 1
                elif data[1] == 1:
                    return
                elif data[1] == 2:
                    data = bf_io.read(2)
                    x, y = x + data[0], y - data[1]
                else:
                    num_of_pixels = data[1]
                    num_to_read = (self._size_from_width(num_of_pixels) + 1) // 2 * 2
                    data = bf_io.read(num_to_read)
                    for i in range(num_of_pixels):
                        self[x, y] = self._extract_from_bytes(data, i)
                        x += 1
            else:
                b = bytes([data[1]])
                for i in range(data[0]):
                    self[x, y] = self._extract_from_bytes(b, i % self.ppb)
                    x += 1

    def read_io(self, bf_io):
        # BMP Header
        data = bf_io.read(14)
        self.BMP_id = data[0:2]
        self.BMP_size = unpack("<I", data[2:6])[0]
        self.BMP_reserved1 = data[6:8]
        self.BMP_reserved2 = data[8:10]
        self.BMP_offset = unpack("<I", data[10:14])[0]

        # DIB Header
        data = bf_io.read(4)
        self.DIB_len = unpack("<I", data[0:4])[0]
        data = bf_io.read(self.DIB_len - 4)
        (
            self.DIB_w,
            self.DIB_h,
            self.DIB_planes_num,
            self.DIB_depth,
            self.DIB_comp,
            self.DIB_raw_size,
            self.DIB_hres,
            self.DIB_vres,
        ) = unpack("<iiHHIIii", data[0:28])

        DIB_plt_num_info = unpack("<I", data[28:32])[0]
        DIB_plt_important_num_info = unpack("<I", data[32:36])[0]
        if self.DIB_len > 40:
            self.DIB_extra = data[36:]

        # Palette
        if self.DIB_depth <= 8:
            if DIB_plt_num_info == 0:
                self.DIB_num_in_plt = 2 ** self.DIB_depth
            else:
                self.DIB_num_in_plt = DIB_plt_num_info
            self.palette = [None for i in range(self.DIB_num_in_plt)]
            for i in range(self.DIB_num_in_plt):
                data = bf_io.read(4)
                colour = bytearray([data[2], data[1], data[0]])
                self.palette[i] = colour

        # In case self.DIB_h < 0 for top-down format.
        if self.DIB_h < 0:
            self.DIB_h = -self.DIB_h
            is_top_down = True
        else:
            is_top_down = False

        self.parray = None
        assert self._init(), "Failed to initialize the image!"

        # Pixels
        if self.DIB_comp == 0:
            # BI_RGB
            for h in range(self.DIB_h):
                y = h if is_top_down else self.DIB_h - h - 1
                data = bf_io.read(self.padded_row_size)
                for x in range(self.DIB_w):
                    if self.DIB_depth <= 8:
                        self[x, y] = self._extract_from_bytes(data, x)
                    else:
                        v = x * 3
                        # BMP colour is in BGR order.
                        self[x, y] = (data[v + 2], data[v + 1], data[v])
        else:
            # BI_RLE8 or BI_RLE4
            self._decode_rle(bf_io)

        return self

    def write_io(self, bf_io, force_40B_DIB=False):
        if force_40B_DIB:
            self.DIB_len = 40
            self.DIB_extra = None

        # Only uncompressed image is supported to write.
        self.DIB_comp = 0

        assert self._init(), "Failed to initialize the image!"

        # BMP Header
        bf_io.write(self.BMP_id)
        bf_io.write(pack("<I", self.BMP_size))
        bf_io.write(self.BMP_reserved1)
        bf_io.write(self.BMP_reserved2)
        bf_io.write(pack("<I", self.BMP_offset))
        # DIB Header
        bf_io.write(
            pack(
                "<IiiHHIIiiII",
                self.DIB_len,
                self.DIB_w,
                self.DIB_h,
                self.DIB_planes_num,
                self.DIB_depth,
                self.DIB_comp,
                self.DIB_raw_size,
                self.DIB_hres,
                self.DIB_vres,
                self.DIB_num_in_plt,
                self.DIB_num_in_plt,
            )
        )
        if self.DIB_len > 40:
            bf_io.write(self.DIB_extra)

        # Palette
        if self.DIB_depth <= 8:
            for colour in self.palette:
                bf_io.write(bytes([colour[2], colour[1], colour[0], 0]))

        # Pixels
        for h in range(self.DIB_h):
            # BMP last row comes first.
            y = self.DIB_h - h - 1
            if self.DIB_depth <= 8:
                d = 0
                for x in range(self.DIB_w):
                    self[x, y] %= self.DIB_num_in_plt
                    # One formula that suits all: 1/2/4/8-bit colour depth.
                    d = (d << (self.DIB_depth % 8)) + self[x, y]
                    if x % self.ppb == self.ppb - 1:
                        # Got a whole byte.
                        bf_io.write(bytes([d]))
                        d = 0
                if x % self.ppb != self.ppb - 1:
                    # Last byte if width does not fit in whole bytes.
                    d <<= (
                        8
                        - self.DIB_depth
                        - (x % self.ppb) * (2 ** (self.DIB_depth - 1))
                    )
                    bf_io.write(bytes([d]))
                    d = 0
            else:
                for x in range(self.DIB_w):
                    r, g, b = self[x, y]
                    bf_io.write(bytes([b, g, r]))
            # Pad row to multiple of 4 bytes with 0x00.
            bf_io.write(b"\x00" * (self.padded_row_size - self.row_size))

        num_of_bytes = bf_io.tell()
        return num_of_bytes

    def load(self, file_path):
        with open(file_path, "rb") as file:
            self.read_io(file)
        return self

    def save(self, file_path, force_40B_DIB=False):
        with open(file_path, "wb") as file:
            num_of_bytes = self.write_io(file, force_40B_DIB)
        return num_of_bytes
