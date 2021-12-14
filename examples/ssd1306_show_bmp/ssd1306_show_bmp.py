# Hardware: ESP32, SSD1306 128x64 I2C screen
#   I2C(1):
#       scl: pin(25)
#       sda: pin(26)
# Required modules:
#   ssd1306: official SSD1306 driver
#   microbmp
# Required files:
#   img_LQ_48x48.bmp

from machine import I2C
from ssd1306 import SSD1306_I2C
from microbmp import MicroBMP


def bmp_to_screen(img, screen, x0, y0):
    for y in range(img.DIB_h):
        for x in range(img.DIB_w):
            screen.pixel(x + x0, y + y0, img[x, y])


i2c = I2C(1)
ssd = SSD1306_I2C(128, 64, i2c)

img_LQ_48x48 = MicroBMP().load("img_LQ_48x48.bmp")
bmp_to_screen(img_LQ_48x48, ssd, 40, 8)
ssd.show()
