#!/usr/bin env python3
# /etc/init.d/neocal.py
### BEGIN INIT INFO
# Provides:		neocal.py
# Required-Start:	$remote_fs $syslog
# Required-Stop:	$remote_fs $syslog
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Daemon which turns a 50-LED NeoPixel strip into a calendar at boot time.
# Description:		Enable service provided by daemon.
### END INIT INFO
import board, neopixel
import datetime, pytz, os.path, time
import threading, atexit, random, json
from astral import LocationInfo
from astral.sun import sun
from time import sleep

# NeoPixel Setup
neopixel_pin    = board.D18 # Set to where DATA line is connected.
neopixel_length = 50  # Set to how many lights there are on the NeoPixel strand.
brightness      = 1.0 # Set how bright in the range [0..1] the NeoPixels shall be.
dow_offset      = 31  # This pixel is where the seven days of week start.
moy_offset      = 37  # This pixel is where the twelve months of year start.
dom_offset      = 31  # This pixel is where the thirty-one days of month start.

# Color Setup - adjust colors to your preference.
# Note: The more white they are and the more pixels are lit, the more current it draws,
# so make sure your power supply provides at least 3amps to your pixels.
off             = (0, 0, 0)       # used for "inactive" pixels, i.e., pixels that aren't lit for today
dow_color_day   = (255, 0, 255)   # magenta
dow_color_night = (255, 0, 0)     # red
moy_color_day   = (255, 255, 0)   # yellow
moy_color_night = (0, 255, 0)     # green
dom_color_day   = (0, 255, 255)   # cyan
dom_color_night = (0, 0, 255)     # blue
black           = off
white           = (255, 255, 255) # for reference - color tuples are in RGB (red, green, blue)

# Location Setup - needed for day/night color transitions. Adjust to your location.
city      = "Oswego"
region    = "USA"
timezone  = "US/Eastern"
longitude = 43.27
latitude  = 76.32

###
### From here, don't touch, or you might break stuff.
###
# Debug mode makes time go by faster.
DEBUG   = False
INTERACTIVE = False # Wait for button press to switch days
COUNTER = 0
DAYS    = [datetime.datetime(1983, 1, 19, 9, 38), datetime.datetime(2009, 8, 13, 16, 30), datetime.datetime(1945, 5, 8, 1, 40), datetime.datetime(1776, 7, 4, 9, 32), datetime.datetime(2063, 4, 4, 23, 15), datetime.datetime(1999, 12, 31, 23, 59), datetime.datetime(1966, 9, 6, 8, 42), datetime.datetime(2013, 12, 5, 18, 53)]

# Global infrastructure. Don't touch.
neocalThread = threading.Thread()
lock         = threading.Lock()
initialized  = False
pixels       = neopixel.NeoPixel(neopixel_pin, neopixel_length, brightness=brightness, pixel_order=neopixel.RGB)
interval     = 15   # Interval between date checks.
timeout      = 0.01 # Transition timing for animations.
if (DEBUG):
   interval  = 5
hueGPIOThread= threading.Thread()
FILEMODE     = False
FILENAME     = "/path/to/hueGPIO.json"
FILEDATE     = datetime.datetime.now()

# Some helper variables to keep track of today and yesterday to enable neat transitions
todayDOW = 0
yesterdayDOW = 0
todayMOY = 0
yesterdayMOY = 0
todayDOM = 0
yesterdayDOM = 0

# Interface function to allow hueGPIO to control "off"
def setHueColor(color, bright):
    global off, brightness
    global neocalThread
    neocalThread.cancel()
    off = int(color[0]), int(color[1]), int(color[2])
    brightness = bright
    if brightness == 0.0:
        off = black
    else:
        pixels.brightness = brightness
    pixels.fill(off)
    neocalThread = threading.Timer(3, run, ())
    neocalThread.start()
    if DEBUG:
        print("New color received from hueGPIO: ", off, ", brightness: ", brightness)


# Interface function to read hueGPIO color changes from json file and control "off"
def loadHueColor():
    global FILEDATE, hueGPIOThread
    if os.path.isfile(FILENAME):
        with open(FILENAME) as json_file:
            modTime = datetime.datetime.fromtimestamp(os.path.getmtime(FILENAME))
            if modTime > FILEDATE:
                FILEDATE = modTime
                data = json.load(json_file)
                color = int(data['color'].split(',')[0]), int(data['color'].split(',')[1]), int(data['color'].split(',')[2])
                bright = float(data['brightness'])
                setHueColor(color, bright)
    hueGPIOThread = threading.Timer(1, loadHueColor(), ())
    hueGPIOThread.start()


# Helper function to make neat transitions. Also turns off yesterday's pixels.
def transition(yesterday, today, targetColor):
   #target and current colors for today's pixel
   targetRed = list(targetColor)[0]
   targetGreen = list(targetColor)[1]
   targetBlue = list(targetColor)[2]
   currentColor = pixels[today]
   currentRed = list(currentColor)[0]
   currentGreen = list(currentColor)[1]
   currentBlue = list(currentColor)[2]

   #if the target color and current color are the same, no need to transition
   if (targetColor == currentColor):
      return

   #target and current colors for yesterday's pixel
   pastColor = pixels[yesterday]
   pastRed = list(pastColor)[0]
   pastGreen = list(pastColor)[1]
   pastBlue = list(pastColor)[2]
   offRed = list(off)[0]
   offGreen = list(off)[1]
   offBlue = list(off)[2]

   #transition the pixels by gradually changing the color values
   while (currentRed != targetRed or currentGreen != targetGreen or currentBlue != targetBlue or offRed != pastRed or offGreen != pastGreen or offBlue != pastBlue):
     #these if-statements transition today's pixel
     if (currentRed < targetRed):
        currentRed += 1
     if (currentRed > targetRed):
        currentRed -= 1
     if (currentGreen < targetGreen):
        currentGreen += 1
     if (currentGreen > targetGreen):
        currentGreen -= 1
     if (currentBlue < targetBlue):
        currentBlue += 1
     if (currentBlue > targetBlue):
        currentBlue -= 1
     currentColor = (currentRed, currentGreen, currentBlue)
     pixels[today] = currentColor

     #these if-statements transition yesterday's pixel
     if (pastRed < offRed):
        pastRed += 1
     if (pastRed > offRed):
        pastRed -= 1
     if (pastGreen < offGreen):
        pastGreen += 1
     if (pastGreen > offGreen):
        pastGreen -= 1
     if (pastBlue < pastBlue):
        pastBlue += 1
     if (pastBlue > offBlue):
        pastBlue -= 1
     pastColor = (pastRed, pastGreen, pastBlue)
     #make sure we don't reverse the transition from above if we change color on the same day
     if (yesterday != today):
        pixels[yesterday] = pastColor

# Interrupt handler that turns pixels off when neotemp exits (SIGTERM). Also unschedules the next thread.
def interrupt():
   global neocalThread
   global pixels
   neocalThread.cancel()
   sleep(1)
   pixels.fill(off)

# Initializes the pixels at startup. Turns them all on and off in a neat animation, partly because we can and partly
# to test if they are all working.
def initPixels():
   global initialized
   if initialized:
      return
   # initialize pixels and set location info
   global neocalThread
   global pixels
   global location
   for n in reversed(range(neopixel_length)):
      pixels[n] = white
      sleep(timeout)
   sleep(1.5)
   for n in range(neopixel_length):
      pixels[n] = black
      sleep(timeout)

   location = LocationInfo(city, region, latitude, longitude)

   # Create neocal thread, start immediately
   neocalThread = threading.Timer(0, run, ())
   neocalThread.start()
   initialized = True

# Main program, which determines the current date and lights the pixels.
# Threading allows us to avoid while(true) loops.
def run():
   global neocalThread
   with lock:
      # run neocal core
      # this is the same as a while(True) loop, as it recursively schedules the next thread
      # but since we're scheduling thread execution, we don't have to sleep nor do we need to loop
      if (DEBUG):
         now = pytz.timezone('UTC').localize(random.choice(DAYS))
         print("DEBUG MODE. Next date = ", now)
         if (INTERACTIVE):
            input("Press any key to continue.")
      else:
         now = pytz.timezone('UTC').localize(datetime.datetime.now())

      s = sun(location.observer, tzinfo=pytz.timezone('UTC'))
      global todayDOW
      global todayMOY
      global todayDOM
      todayDOW = dow_offset + now.weekday()  # weekday() is a method and zero-based, i.e. Monday = 0
      todayMOY = moy_offset + now.month
      todayDOM = dom_offset - now.day

      # determine if it's time for dusk or dawn colors
      if (now <= s['sunrise'] or now >= s['sunset']):
         dow_color = dow_color_night
         moy_color = moy_color_night
         dom_color = dom_color_night
         if (DEBUG):
            print("now:", now, "sunrise: ", s["sunrise"], "sunset:", s["sunset"], "Setting NIGHT colors")
      else:
         dow_color = dow_color_day
         moy_color = moy_color_day
         dom_color = dom_color_day
         if (DEBUG):
            print("now, ", now, "sunrise:", s["sunrise"], "sunset:", s["sunset"], "Setting DAY colors")

      # debug mode - test transitions between days and colors
      global COUNTER
      if (DEBUG and COUNTER % 2 == 0):
         COUNTER += 1
         dow_color = dow_color_night
         moy_color = moy_color_night
         dom_color = dom_color_night
      elif (DEBUG and COUNTER % 1 == 0):
         COUNTER += 1
         dow_color = dow_color_day
         moy_color = moy_color_day
         dom_color = dow_color_day

      global yesterdayDOW
      global yesterdayMOY
      global yesterdayDOM
      dow_thread = threading.Thread(target=transition, args=(yesterdayDOW, todayDOW, dow_color))
      moy_thread = threading.Thread(target=transition, args=(yesterdayMOY, todayMOY, moy_color))
      dom_thread = threading.Thread(target=transition, args=(yesterdayDOM, todayDOM, dom_color))
      dow_thread.start()
      moy_thread.start()
      dom_thread.start()

      yesterdayDOW = todayDOW
      yesterdayMOY = todayMOY
      yesterdayDOM = todayDOM

   # recursively schedule next thread
   neocalThread = threading.Timer(interval, run, ())
   neocalThread.start()

#start neocal
initPixels()
# when neocal exits (SIGTERM), unschedule the next thread
atexit.register(interrupt)
#END.
