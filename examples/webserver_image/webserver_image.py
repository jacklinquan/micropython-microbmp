# Hardware: ESP32
# Required modules:
#   picoweb
#   pkg_resources (required by picoweb)
#   logging (required by picoweb)
#   microbmp
# Required actions:
#   Set essid and password of your own wifi

import network
from io import BytesIO
import picoweb
import logging
from microbmp import MicroBMP


essid = "YOUR_ESSID"
password = "YOUR_PASSWORD"


def set_img_colour(colour_idx):
    for y in range(32):
        for x in range(32):
            img[x, y] = colour_idx


def connect_wifi(essid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(essid, password)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())
    return wlan


app = picoweb.WebApp(__name__)


@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite(b"Dynamic image: <img src='img.bmp'><br />")


@app.route("/img.bmp")
def squares(req, resp):
    yield from picoweb.start_response(resp, "image/bmp")
    set_img_colour(parameters["colour"])
    bf_io = BytesIO()
    img.write_io(bf_io)
    bf_io.seek(0)
    yield from resp.awrite(bf_io.read())
    parameters["colour"] = (parameters["colour"] + 1) % 3


parameters = {"colour": 0}  # 0:Red, 1:Green, 2:Blue
img = MicroBMP(32, 32, 2)  # 2-bit(max 4 colours) 32x32 image
img.palette = [
    bytearray([0xFF, 0, 0]),
    bytearray([0, 0xFF, 0]),
    bytearray([0, 0, 0xFF]),
    bytearray([0, 0, 0]),
]


wlan = connect_wifi(essid, password)
logging.basicConfig(level=logging.INFO)
app.run(debug=True, host=wlan.ifconfig()[0])
