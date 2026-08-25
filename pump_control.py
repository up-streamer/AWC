import asyncio
from machine import Pin
from time import sleep_ms

ON = True
OFF = False

class PumpControl:
    def __init__(self, sampleInterval = 1000):
        self.startPerct = 0
        self.stopPerct = 100
        self.sampleInterval = sampleInterval
        self.headTkLevel = 0
        self.headTkErr = 0
        self.flowOk = 0
        self.err = 0
        self.mode = 'Auto'
        self.pumpCommand = 'OFF'
        self.pump = Pin(2, Pin.OUT)
        self.pump.off()

    def start(self):
        asyncio.create_task(self._run(self.sampleInterval))

    def _pumpSwitch(self, sw):
        if sw:
            self.pump.on()
            self.pumpCommand = 'ON'
        else:
            self.pump.off()
            self.pumpCommand = 'OFF'

    async def _retry(self, sampleInterval):
        self.err = 2 #Retry
        self._pumpSwitch(OFF)
        for attempt in range(3):
            for delay in range (10): #Was 15
                if self.mode == 'Auto' and not self.headTkErr:
                    await asyncio.sleep_ms(sampleInterval)
                else:
                    return

            self._pumpSwitch(ON)

            for delay in range (10):  #Was 30
                if self.mode == 'Auto' and not self.headTkErr:
                    await asyncio.sleep_ms(sampleInterval)
                else:
                    self._pumpSwitch(OFF)
                    return

            if self.flowOk == 0: # Have flow! All good.
                self.err = 0
                return    # Stop retries
            else:
                self._pumpSwitch(OFF)

        self.err = 4 #Time out no flow
        return

    async def _run(self, sampleInterval):
        await asyncio.sleep_ms(6000)
        while True:
            levelPerct = float(self.headTkLevel)
            if self.headTkErr and (self.pumpCommand == 'ON'):
                self.err = 3 
            err = self.err + self.flowOk

            if self.mode == 'Auto':
                if levelPerct >= self.stopPerct:
                        if self.pumpCommand == 'ON':
                            self._pumpSwitch(OFF)
                if not err:   
                    if levelPerct <= self.startPerct:
                        if self.pumpCommand == 'OFF':
                            self._pumpSwitch(ON)
                            for delay in range (10):
                                if not (self.mode == 'Manual'):
                                    await asyncio.sleep_ms(sampleInterval)
                else:
                    if self.err == 1:
                        self.err = 0 # Reset Caution message
                        self._pumpSwitch(OFF)

                    if (not self.headTkErr) and (self.flowOk == 1) and self.pumpCommand == 'ON': 
                        await self._retry(sampleInterval)
                    else:
                        self._pumpSwitch(OFF)

            # Out of Auto mode #
            if (self.mode == 'Completar') and (self.pumpCommand == 'ON'): # Hack, necessary to activate pump in 'Completar'
                self.mode = 'Auto'
                self._pumpSwitch(ON)
                for delay in range (10):    ###  Not necessary... test it
                    if not (self.mode == 'Manual'):
                        await asyncio.sleep_ms(sampleInterval)

            if self.mode == 'Manual':
                if self.pumpCommand == 'OFF':
                    self.pump.off()
                    self.err = 0 # Cleared errors.
                if self.pumpCommand == 'ON':
                    self.pump.on() 
                    self.err = 1 # Caution msg Pump running in manual mode

            await asyncio.sleep_ms(sampleInterval)
