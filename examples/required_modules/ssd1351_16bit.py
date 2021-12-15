import framebuf
import utime
import gc
import micropython
from uctypes import addressof
import sys
# https://github.com/peterhinch/micropython-nano-gui/issues/2
# The ESP32 does not work reliably in SPI mode 1,1. Waveforms look correct.
# Keep 0,0 on STM as testing was done in that mode.
_bs = 0 if sys.platform == 'esp32' else 1  # SPI bus state

# SPI baudrate: Pyboard can produce 10.5MHz or 21MHz. Datasheet gives max of 20MHz.
# Attempt to use 21MHz failed but might work on a PCB or with very short leads.
class SSD1351(framebuf.FrameBuffer):
    # Convert r, g, b in range 0-255 to a 16 bit colour value RGB565
    #  acceptable to hardware: rrrrrggggggbbbbb
    @staticmethod
    def rgb(r, g, b):
        return ((r & 0xf8) << 5) | ((g & 0x1c) << 11) | (b & 0xf8) | ((g & 0xe0) >> 5)

    def __init__(self, spi, pincs, pindc, pinrs, height=128, width=128):
        if height not in (96, 128):
            raise ValueError('Unsupported height {}'.format(height))
        self.spi = spi
        self.rate = 12000000  # See baudrate note above.
        self.pincs = pincs
        self.pindc = pindc  # 1 = data 0 = cmd
        self.height = height  # Required by Writer class
        self.width = width
        # Save color mode for use by writer_gui (blit)
        self.mode = framebuf.RGB565
        gc.collect()
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, self.mode)
        self.mvb = memoryview(self.buffer)
        pinrs(0)  # Pulse the reset line
        utime.sleep_ms(1)
        pinrs(1)
        utime.sleep_ms(1)
        # See above comment to explain this allocation-saving gibberish.
        self._write(b'\xfd\x12\xfd\xb1\xae\xb3\xf1\xca\x7f\xa0\x74'\
        b'\x15\x00\x7f\x75\x00\x7f\xa1\x00\xa2\x00\xb5\x00\xab\x01'\
        b'\xb1\x32\xbe\x05\xa6\xc1\xc8\x80\xc8\xc7\x0f'\
        b'\xb4\xa0\xb5\x55\xb6\x01\xaf', 0)
        self.show()
        gc.collect()

    def _write(self, mv, dc):
        self.spi.init(baudrate=self.rate, polarity=_bs, phase=_bs)
        self.pincs(1)
        self.pindc(dc)
        self.pincs(0)
        self.spi.write(bytes(mv))
        self.pincs(1)

    # Write lines from the framebuf out of order to match the mapping of the
    # SSD1351 RAM to the OLED device.
    def show(self):
        mvb = self.mvb 
        bw = self.width * 2  # Width in bytes
        self._write(b'\x5c', 0)  # Enable data write
        if self.height == 128:
            for l in range(128):
                l0 = (95 - l) % 128  # 95 94 .. 1 0 127 126 .. 96
                start = l0 * self.width * 2
                self._write(mvb[start : start + bw], 1)  # Send a line
        else:
            for l in range(128):
                if l < 64:
                    start = (63 -l) * self.width * 2  # 63 62 .. 1 0
                elif l < 96:
                    start = 0
                else:
                    start = (191 - l) * self.width * 2  # 127 126 .. 95
                self._write(mvb[start : start + bw], 1)  # Send a line