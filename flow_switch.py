import asyncio
from machine import Pin
from time import sleep_ms

class flowSw:
    def __init__(self, sampleInterval = 5000): # was 10000
        self.pumpCmd = 'OFF'
        self.err = 0
        self.sampleInterval = sampleInterval
        self.flowSw = Pin(4, Pin.IN, Pin.PULL_UP)

    def start(self):
        asyncio.create_task(self._run(self.sampleInterval))

    async def _run(self, sampleInterval):
        _flowSw = False
        while True:
            if self.pumpCmd == 'ON':
                await asyncio.sleep_ms(sampleInterval) # Delay time to check
                _flowSw = self.flowSw.value()
                if _flowSw and self.pumpCmd == 'ON':
                    self.err = 0
                else:
                    self.err = 1 # Waiting flowing on headTk
            else:
                _flowSw1st = self.flowSw.value()
                await asyncio.sleep_ms(sampleInterval) # Delay time to check
                _notFlowSw = not (_flowSw1st + self.flowSw.value())
                if _notFlowSw and self.pumpCmd == 'OFF': # Check pump is still OFF?
                    self.err = 0
                elif (not _notFlowSw) and self.pumpCmd == 'OFF': ### To cover other possibilites...
                    self.err = 2 # Flow sensor fault            ### Pump turned on during await 

            print("Flow Switch = " + str(_flowSw))
            print("  Flow Error = " + str(self.err))
        