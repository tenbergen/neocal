# neocal
A perpetual calendar for Raspberry Pi using neopixel LED lights.

## Hardware Requirements
- 1 WS2811 RGB LED pixel strip with at least 50 LEDs (example: https://www.amazon.com/dp/B06XD72LYM/ref=cm_sw_em_r_mt_dp_U_WfHIEbBTP5C4D)
- 1 5V, 5A (min) power supply (example: https://www.amazon.com/dp/B01LXN7MN3/ref=cm_sw_em_r_mt_dp_U_1iHIEbHJZGBM1)
- 1 Raspberry Pi (example: https://www.adafruit.com/product/3400)
- 1 MicroSD card (example: https://www.amazon.com/dp/B073K14CVB/ref=cm_sw_em_r_mt_dp_U_UnHIEb4XJDQ89)
- 1 Raspberry Pi protoboard (https://www.amazon.com/dp/B07C54DP8T/ref=cm_sw_em_r_mt_dp_U_NoHIEbE5HTDNE)
- 1 74AHCT125 Level-Shifter (example: https://www.adafruit.com/product/1787)
- 1 40-pin header (example: https://www.amazon.com/dp/B0756KM7CY/ref=cm_sw_em_r_mt_dp_U_JtHIEbF4A8MR4)
- soldering equipment and some extra wires

## Hardware assembly
1. Solder the 40-pin header to the Raspberry Pi.
2. Solder the Level Shifter to the protoboard following these directions: https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring
3. Solder the RGB LED strip to the +5V, Ground, and DATA pins on your protoboard.

## Software Dependencies
- Raspbian Strech or higher
- root privileges
- python3 with pip3
- python3 modeules: adafruit-circuitpython-neopixel and rpi_ws281x (see https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage)

## Requirements
neocal requires to be executed with sudo, as adafruit neopixel library requires elevated permissions. It also requries python3.

## Installation

Execute on Raspbian stretch or newer:
```
git clone https://github.com/tenbergen/neocal.git
cd neocal
sudo sh install.sh
```
The service will start immediately and after reboot.

### Control the service
To start/stop the service, simply run:
```
sudo systemctl [start|stop] sysup.service
```

## Known issues
Lights won't go out if you stop the service or the service fails.

## Contribute
Share the love and improve this thing. I'm sure there's plenty ways to make it better. My main concern is making somehting easy to use and versatile.