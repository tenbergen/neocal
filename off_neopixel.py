import board, neopixel

length = 50

pixels = neopixel.NeoPixel(board.D18, length, pixel_order=neopixel.RGB)
pixels.fill((0, 0, 0))
