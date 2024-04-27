import asyncio
from machine import Pin
from time import sleep_ms

ON = True
OFF = False

class PumpControl:
    def __init__(self, startPerct, stopPerct, sampleInterval = 1000):
        self.startPerct = startPerct
        self.stopPerct = stopPerct
        self.sampleInterval = sampleInterval
        self.headTkLevel = 0
        self.headTkErr = 0
        self.flowOk = True
        self.err = 0
        self.mode = 'Auto'
        self.pumpCommand = 'OFF'
        self.pump = Pin(2, Pin.OUT)
        self.pump.off()
        if startPerct >= stopPerct:
            self.err = 1           #Setup limits inverted
        #asyncio.create_task(self._run(sampleInterval))
            
    def start(self):
        asyncio.create_task(self._run(self.sampleInterval))

    def _pumpSwitch(self, sw):
        if sw:
            self.pump.on()
            self.pumpCommand = 'ON'
        else:
            self.pump.off()
            self.pumpCommand = 'OFF'
        print("pump SW = " + str(sw))

    async def _retry(self, sampleInterval):
        self.err = 3 #Retry
        for attempt in range(3):
            for delay in range (10): #Was 15
                if self.mode == 'Auto' and not self.headTkErr:
                    await asyncio.sleep_ms(sampleInterval)
                else:
                    self._pumpSwitch(OFF)
                    return

            self._pumpSwitch(ON)

            for delay in range (10):  #Was 30
                if self.mode == 'Auto' and not self.headTkErr:
                    await asyncio.sleep_ms(sampleInterval)
                else:
                    self._pumpSwitch(OFF)
                    return

            if self.flowOk:
                self.err = 0
                return    # Stop retries
            else:
                self._pumpSwitch(OFF)

        self.err = 5 #Time out no flow
        self._pumpSwitch(OFF)
        return

    async def _run(self, sampleInterval):
        while True:
            levelPerct = float(self.headTkLevel)
            err = self.err + self.headTkErr

            if self.mode == 'Auto':
                if err == 0  and self.flowOk == True:
                    if levelPerct <= self.startPerct:
                        if self.pumpCommand == 'OFF':
                            self._pumpSwitch(ON)
                    elif(levelPerct >= self.stopPerct):
                        if self.pumpCommand == 'ON':
                            self._pumpSwitch(OFF)
                    print("pump command from pump = " + self.pumpCommand)
                    print("level from pump = " + str(levelPerct))
                    print("stop level from pump " + str(self.stopPerct))
                    print("headTkLevel from pump = " + str(self.headTkLevel))
                    print("________________________________")
                else:
                    if self.headTkErr:
                        self.err = 4

                    if self.err == 2:
                        self.err = 0 # Reset Caution message

                    self._pumpSwitch(OFF)

                    if not (err or self.flowOk) and levelPerct <= self.startPerct:
                        await self._retry(sampleInterval)

            if (self.mode == 'Completar') and (self.pumpCommand == 'ON'):      
                self.pump.on()
 
            if self.mode == 'Manual':
                if self.pumpCommand == 'OFF':
                    self.pump.off()
                    self.err = 0 # Cleared errors.
                if self.pumpCommand == 'ON':
                    self.pump.on()
                    self.err = 2 # Caution! Pump running without protection
            await asyncio.sleep_ms(sampleInterval)
