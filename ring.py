# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
# Will color all the lights different primary colors.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
import math

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI


# Configure the count of pixels:
PIXEL_COUNT = 50

# The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.

# Specify a software SPI connection for Raspberry Pi on the following pins:
PIXEL_CLOCK = 18
PIXEL_DOUT  = 23
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=PIXEL_CLOCK, do=PIXEL_DOUT)

BRIGHTNESS = 0.5

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
#SPI_PORT   = 0
#SPI_DEVICE = 0
#pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Clear all the pixels to turn them off.
pixels.clear()
pixels.show()  # Make sure to call show() after changing any pixels!

for i in range(PIXEL_COUNT-1):
    pixels.clear()
    pixels.set_pixel_rgb(i,int(math.floor(255 * BRIGHTNESS)),int(math.floor(255 * BRIGHTNESS)),int(math.floor(255 * BRIGHTNESS)))
    pixels.show()
    time.sleep(1)
# Not used but you can also read pixel colors with the get_pixel_rgb function:
#r, g, b = pixels.get_pixel_rgb(0)  # Read pixel 0 red, green, blue value.
