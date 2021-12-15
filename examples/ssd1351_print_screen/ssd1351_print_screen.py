# Hardware: ESP32, SSD1351 128x128 SPI screen
#   SPI(2):
#       sck: pin(18)
#       mosi: pin(23)
#       miso: pin(19) not used
# Required modules:
#   ssd1351_16bit (RGB565 format)
#   microbmp

from machine import Pin, SPI
from ssd1351_16bit import SSD1351
from microbmp import MicroBMP


def rgb565_to_rgb(c):
    r = (c >> 8) & 0x1F
    g = ((c << 3) & 0x38) + ((c >> 13) & 0x7)
    b = (c >> 3) & 0x1F
    r = (r * 255 + 15) // 31
    g = (g * 255 + 31) // 63
    b = (b * 255 + 15) // 31
    return r, g, b


def screen_to_bmp(screen, img):
    plt_dict = {}
    plt_len = 0
    for y in range(img.DIB_h):
        for x in range(img.DIB_w):
            rgb = rgb565_to_rgb(screen.pixel(x, y))
            if rgb not in plt_dict:
                img.palette[plt_len] = bytearray(rgb)
                plt_dict[rgb] = plt_len
                plt_len += 1
            img[x, y] = plt_dict[rgb]


pindc = Pin(17, Pin.OUT, value=0)
pincs = Pin(5, Pin.OUT, value=1)
pinrs = Pin(16, Pin.OUT, value=1)
spi = SPI(2, baudrate=12000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
ssd = SSD1351(spi, pincs, pindc, pinrs)

ssd.fill(0)
ssd.text("Hello, World!", 0, 0, ssd.rgb(255, 255, 255))
ssd.text("0123456789", 0, 16, ssd.rgb(255, 0, 0))
ssd.text("ABCDEFGHIJKLMNOP", 0, 32, ssd.rgb(0, 255, 0))
ssd.text("QRSTUVWXYZ", 0, 48, ssd.rgb(0, 0, 255))
ssd.text("abcdefghijklmnop", 0, 64, ssd.rgb(255, 255, 0))
ssd.text("qrstuvwxyz", 0, 80, ssd.rgb(255, 0, 255))
ssd.text("~!@#$%^&*()_-+=`", 0, 96, ssd.rgb(0, 255, 255))
ssd.text("[]{}\\|;:'\"<>,./?", 0, 112, ssd.rgb(127, 127, 127))
ssd.show()

# Create a 4-bit BMP image, size 128x128
img_4b_128x128 = MicroBMP(128, 128, 4)
# It takes seconds to copy the screen to the image.
screen_to_bmp(ssd, img_4b_128x128)
# It takes seconds to save the image to the file system.
img_4b_128x128.save("img_4b_128x128.bmp")
