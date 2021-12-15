# Hardware: ESP32, SSD1351 128x128 SPI screen
#   SPI(2):
#       sck: pin(18)
#       mosi: pin(23)
#       miso: pin(19) not used
# Required modules:
#   ssd1351_16bit (RGB565 format)
#   microbmp
# Required files:
#   img_LQ_4b_48x48.bmp

from machine import Pin, SPI
from ssd1351_16bit import SSD1351
from microbmp import MicroBMP


def bmp_to_screen(img, screen, x0, y0):
    for y in range(img.DIB_h):
        for x in range(img.DIB_w):
            r, g, b = img.palette[img[x, y]]
            screen.pixel(x + x0, y + y0, screen.rgb(r, g, b))


pindc = Pin(17, Pin.OUT, value=0)
pincs = Pin(5, Pin.OUT, value=1)
pinrs = Pin(16, Pin.OUT, value=1)
spi = SPI(2, baudrate=12000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
ssd = SSD1351(spi, pincs, pindc, pinrs)

ssd.fill(0)
img_LQ_4b_48x48 = MicroBMP().load("img_LQ_4b_48x48.bmp")
bmp_to_screen(img_LQ_4b_48x48, ssd, 40, 40)
ssd.show()
