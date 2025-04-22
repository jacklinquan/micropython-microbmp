# micropython-microbmp
[![PayPal Donate][paypal_img]][paypal_link]
[![PyPI version][pypi_img]][pypi_link]
[![Downloads][downloads_img]][downloads_link]

  [paypal_img]: https://github.com/jacklinquan/images/blob/master/paypal_donate_badge.svg
  [paypal_link]: https://www.paypal.me/jacklinquan
  [pypi_img]: https://badge.fury.io/py/micropython-microbmp.svg
  [pypi_link]: https://badge.fury.io/py/micropython-microbmp
  [downloads_img]: https://pepy.tech/badge/micropython-microbmp
  [downloads_link]: https://pepy.tech/project/micropython-microbmp

[Try `micropython-microbmp` in browser.](https://jacklinquan.github.io/micropython-microbmp/)

A small Python module for BMP image processing.
 
It supports BMP image of 1/2/4/8/24-bit colour depth.

Loading supports compression method:

- 0(BI_RGB, no compression)
- 1(BI_RLE8, RLE 8-bit/pixel)
- 2(BI_RLE4, RLE 4-bit/pixel)

Saving only supports compression method 0(BI_RGB, no compression).

The [API][api_link] is compatible with the CPython version [microbmp][microbmp_link].
As a pure python module, it's not fast. But it opens up the possibility to save images.
It is especially useful for small IR cameras/sensors.

  [api_link]: https://microbmp.readthedocs.io/en/latest/?badge=latest
  [microbmp_link]: https://github.com/jacklinquan/microbmp

## Where this module can be useful
This module can be useful in many scenarios, not limited to the list below:

- To show BMP images on the screen.
    It supports 1/2/4/8/24-bit colour depth and RLE compression(4-bit and 8-bit).
    If the number of colours used in an image is small, it can be much compact.
- To print the screen.
    A screen or any `framebuf.FrameBuffer` object can be saved as a BMP image.
- To save camera or IR thermal camera images.
    For projects that involve MLX90640 or AMG88xx, the IR images can be saved.
- To generate dynamic BMP images for web servers.
    This module also can write BMP images to BytesIO.
    So it does NOT have to save the images in the file system.
    A combination of web server and IR camera can show IR image dynamically in the browser.

## Installation
The Python file `microbmp.py` can be installed on target hardware with `mpremote`:
```shell
pip install mpremote
mpremote mip install github:jacklinquan/micropython-microbmp
```
Alternatively just copy microbmp.py to the MicroPython device.

## Usage
```Python
>>> from microbmp import MicroBMP
>>> img_24b_2x2 = MicroBMP(2, 2, 24)  # Create a 2(width) by 2(height) 24-bit image.
>>> img_24b_2x2.palette  # 24-bit image has no palette.
>>> img_24b_2x2.parray  # Pixels are arranged horizontally (top-down) in RGB order.
bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
>>> img_24b_2x2[1, 1] = 255, 255, 255  # Access 1 pixel (R, G, B): img[x, y]
>>> img_24b_2x2[0, 1, 0] = 255  # Access 1 primary colour of 1 pixel (Red): img[x, y, c]
>>> img_24b_2x2[1, 0, 1] = 255  # (Green)
>>> img_24b_2x2[0, 0, 2] = 255  # (Blue)
>>> img_24b_2x2.save("img_24b_2x2.bmp")
70
>>> new_img_24b_2x2 = MicroBMP().load("img_24b_2x2.bmp")
>>> new_img_24b_2x2.palette
>>> new_img_24b_2x2.parray
bytearray(b'\x00\x00\xff\x00\xff\x00\xff\x00\x00\xff\xff\xff')
>>> print(new_img_24b_2x2)
BMP image, RGB, 24-bit, 2x2 pixels, 70 bytes
>>> img_1b_3x2 = MicroBMP(3, 2, 1)  # Create a 3(width) by 2(height) 1-bit image.
>>> img_1b_3x2.palette  # Each colour is in the order of (R, G, B)
[bytearray(b'\x00\x00\x00'), bytearray(b'\xff\xff\xff')]
>>> img_1b_3x2.parray  # Each bit stores the colour index in HLSB format.
bytearray(b'\x00')
>>> " ".join(["{:0>8}".format(bin(byte)[2:]) for byte in img_1b_3x2.parray])
'00000000'
>>> img_1b_3x2[1, 0] = 1  # Access 1 pixel (index): img[x, y]
>>> img_1b_3x2[1, 1] = 1
>>> img_1b_3x2[2, 1] = 1
>>> img_1b_3x2.save("img_1b_3x2.bmp")
70
>>> new_img_1b_3x2 = MicroBMP().load("img_1b_3x2.bmp")
>>> new_img_1b_3x2.palette
[bytearray(b'\x00\x00\x00'), bytearray(b'\xff\xff\xff')]
>>> new_img_1b_3x2.parray
bytearray(b'L')
>>> " ".join(["{:0>8}".format(bin(byte)[2:]) for byte in new_img_1b_3x2.parray])
'01001100'
>>> print(new_img_1b_3x2)
BMP image, indexed, 1-bit, 3x2 pixels, 70 bytes
```
