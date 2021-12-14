# Hardware: ESP32, SSD1306 128x64 I2C screen
#   I2C(1):
#       scl: pin(25)
#       sda: pin(26)
# Required modules:
#   ssd1306: official SSD1306 driver
#   microbmp

from machine import I2C
from ssd1306 import SSD1306_I2C
from microbmp import MicroBMP


def screen_to_bmp(screen, img):
    for y in range(img.DIB_h):
        for x in range(img.DIB_w):
            img[x, y] = screen.pixel(x, y)


i2c = I2C(1)
ssd = SSD1306_I2C(128, 64, i2c)

ssd.text("Hello, World!", 0, 0)
ssd.text("0123456789", 0, 8)
ssd.text("ABCDEFGHIJKLMNOP", 0, 16)
ssd.text("QRSTUVWXYZ", 0, 24)
ssd.text("abcdefghijklmnop", 0, 32)
ssd.text("qrstuvwxyz", 0, 40)
ssd.text("~!@#$%^&*()_-+=`", 0, 48)
ssd.text("[]{}\\|;:'\"<>,./?", 0, 56)
ssd.show()

# Create a 1-bit BMP image, size 128x64
img_1b_128x64 = MicroBMP(128, 64, 1)
# It takes seconds to copy the screen to the image.
screen_to_bmp(ssd, img_1b_128x64)
# It takes seconds to save the image to the file system.
img_1b_128x64.save("img_1b_128x64.bmp")
