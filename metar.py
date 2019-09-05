import requests
from enum import Enum
import xml.etree.ElementTree as et
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
import time
import sys
import argparse

URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString={}&mostRecentForEachStation=constraint&hoursBeforeNow=3"
BRIGHTNESS = 0.5
VERBOSE = False
LED_SINGLETON = None

class Station:
    icao = ""
    flight_rules = "NONE"
    position = 0

    VFR_COLOR = (0,255,0)
    MVFR_COLOR = (0,0,255)
    IFR_COLOR = (255,0,0)
    LIFR_COLOR = (255,0,144)
    NONE_COLOR = (0,0,0)
    
    def __init__(self, icao, pos):
        self.icao = icao
        self.position = pos

    def setFlightRules(self, flight_rules):
        self.flight_rules = flight_rules

    def getColor(self):
        if self.flight_rules == 'VFR':
            return self.VFR_COLOR
        elif self.flight_rules == 'MVFR':
            return self.MVFR_COLOR
        elif self.flight_rules == 'IFR':
            return self.IFR_COLOR
        elif self.flight_rules == 'LIFR':
            return self.LIFR_COLOR
        else:
            if VERBOSE:
                print "No category found for {}".format(self.icao)
            return self.NONE_COLOR

    def __repr__(self):
        return "{},{},{}".format(self.icao, self.flight_rules, self.pos)

def readStations(filename):
    stations = []
    f = open(filename)
    lines = f.read().splitlines()
    numRead = 0
    for line in lines:
        # ignore comments in file
        if line[0] != '#':
            split = line.split()
            if len(split) != 2:
                print "Error encountered with line \"{}\"".format(line)
                continue
            numRead = numRead + 1
            stations.append((split[0], int(split[1])))
    print "{} stations read from {}".format(numRead, filename)
    f.close()
    return stations

def createStations(stationList):
    sDict = {}
    for s in stationList:
        icao, pos = s
        sDict[icao] = Station(icao, pos)
    print "{} Stations created".format(len(sDict))
    return sDict

def getMetars(stationDict):
    fullUrl = URL.format(','.join(map(lambda s: s.icao, stationDict.values())))
    if VERBOSE:
        print "Full url: {}".format(fullUrl)
    r = requests.get(fullUrl)
    root = et.fromstring(r.content)
    # iterate over all metars
    num = 0
    for metar in root.iter('METAR'):
        num = num + 1
        station_id = metar.find('station_id').text
        flight_category = metar.find('flight_category').text
        if VERBOSE:
            print station_id, flight_category

        stationDict[station_id].setFlightRules(flight_category)

    print "Downloaded {} METARS".format(num)

def updateLEDs(stationDict):
    leds = getLeds()
    leds.clear()
    leds.show()
    for station in stationDict.values():
        r,g,b = station.getColor()
        pos = station.position
        leds.set_pixel_rgb(pos, int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))
    leds.show()

def getLeds():
    global LED_SINGLETON
    if LED_SINGLETON is None:
        numLed = 49
        clk = 18
        dout = 23
        LED_SINGLETON = Adafruit_WS2801.WS2801Pixels(numLed, clk=clk, do=dout)
        print "Created strip of {} LEDs".format(LED_SINGLETON.count())
    return LED_SINGLETON

def setAllLeds(color):
    led = getLeds()
    r,g,b = color
    led.clear()
    for i in range(led.count()):
        led.set_pixel_rgb(i, int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))
    led.show()

def main(args):
    stationList = readStations("west_airports.txt")
    stationDict = createStations(stationList)
    getMetars(stationDict)
    updateLEDs(stationDict)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--testmode", dest="testmode", choices=["vfr","mvfr","ifr","lifr","all"])
    parser.add_argument("-v","--verbose", action="store_true")
    args = parser.parse_args()
    
    if args.verbose:
        VERBOSE = True
    
    if args.testmode == "vfr":
        print "RUNNING IN VFR TEST MODE"
        setAllLeds(Station.VFR_COLOR)
    elif args.testmode == "mvfr":
        print "RUNNING IN MVFR TEST MODE"
        setAllLeds(Station.MVFR_COLOR)
    elif args.testmode == "ifr":
        print "RUNNING IN IFR TEST MODE"
        setAllLeds(Station.IFR_COLOR)
    elif args.testmode == "lifr":
        print "RUNNING IN LIFR TEST MODE"
        setAllLeds(Station.LIFR_COLOR)
    elif args.testmode == "all":
        print "RUNNING ALL COLORS"
        setAllLeds(Station.VFR_COLOR)
        time.sleep(2)
        setAllLeds(Station.MVFR_COLOR)
        time.sleep(2)
        setAllLeds(Station.IFR_COLOR)
        time.sleep(2)
        setAllLeds(Station.LIFR_COLOR)
        time.sleep(2)
        setAllLeds(Station.NONE_COLOR)
    else:
        main(args)
