# Author: Ricardo Santos
# Date: September 7, 2023

# Load the machine module in order to access the hardware
# import machine
from machine import Pin
from machine import UART
from time import sleep_ms
from micropython import const
import asyncio

_PAUSE_MS = const(400)  # AJ-SR04M Acquisition delay

class AJ_SR04:
    def __init__(self, COM = 2, sampleInterval = 2000):
        self.distance = None
        self.err = None
        _lastGoodDistance = None
        _lastGoodlevel = 0
        if COM == 1:
            self.uart = UART(1, 9600, bits=8, parity=None, stop=1, tx=18, rx=5)
        else:
            self.uart = UART(2, 9600, bits=8, parity=None, stop=1, tx=17, rx=16) # Was UART(2...
        self.measurements = Measurements(974, 250, 1000)
        asyncio.create_task(self._run(sampleInterval))
        
    def __iter__(self):  # Await 1st reading
        while self.distance is None:
            yield from asyncio.sleep(0)
            
    async def _run(self, sampleInterval):
        if (sampleInterval - _PAUSE_MS) <= 0:
            sampleInterval = 0
        else:
            sampleInterval = sampleInterval - _PAUSE_MS
        while True:
            await asyncio.sleep_ms(sampleInterval)
            self.distance = await self._updDistance()
            self.measurements.__updMeasurements(self.distance)
            if self.err == 0: # Error msg priority sensor error > measurements error
                self.err = self.measurements.err
                    
    async def _updDistance(self):
        global _lastGoodDistance
        self.uart.write(b'\x01')
        await asyncio.sleep_ms(_PAUSE_MS)
        # if there is character in receive serial buffer
        if self.uart.any() >= 4: # before was  == 4
            # Read 4 the characters to raw_distance variable
            raw_distance = self.uart.read()
            
            #print("Raw Distance = " + str(raw_distance))
            checkData = (raw_distance[0]+raw_distance[1]+raw_distance[2]+1) & 0x00ff
            #print((raw_distance[0]+raw_distance[1]+raw_distance[2]+1) & 0x00ff)
            #print("sum: " + str(raw_distance[3]))
            #print("checkData =" + str(checkData))
            if checkData == raw_distance[3]:
                hi_data = raw_distance[1] << 8
                lo_data = raw_distance[2]
                rawDistance = hi_data + lo_data
                if rawDistance <= 10000:
                    self.err = 0
                    _lastGoodDistance = self.distance
                    return rawDistance
                else:
                    self.err = 2 # No echo detected
                    return _lastGoodDistance
        else:
            self.err = 1 # Data Check error, CRC fail
            return _lastGoodDistance
            #raise OSError('Sensor Failed')
                    
class Measurements:
    def __init__(self, max_distance, min_distance, max_volume):
        self.level = 0
        self.percentage = 0
        self.volume = 0
        self.max_volume = max_volume
        self.max_distance = max_distance # Min level
        self.min_distance = min_distance # Max level
        self.max_level = self.max_distance - self.min_distance
        self.tolerance = (self.max_distance - self.min_distance) * 0.05
        global _lastGoodlevel
        _lastGoodlevel = 0
          
    def __updMeasurements(self, distance):
        if self.max_distance > self.min_distance:
            self.err = 0
        else:
            self.err = 3 # distance values reverse
            
        def calc(dist):
            global _lastGoodlevel
            if self.err == 0:
                if (dist < (self.max_distance + self.tolerance)) and (dist > (self.min_distance - self.tolerance)): # Good reading
                    level = self.max_distance - dist
                    self.err == 0
                    _lastGoodlevel = level
                    return level
                else:
                    self.err = 4  # Out of tolerance
                    return _lastGoodlevel
            else:
                return _lastGoodlevel
                
        self.err = 0
        self.level = calc(distance)
        
        proportion = (self.level / self.max_level ) 
        self.percentage = '{:.1f}'.format(proportion * 100)
        self.volume = '{:.1f}'.format(proportion * self.max_volume)
        