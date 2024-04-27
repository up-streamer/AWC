import asyncio
from machine import Pin
from time import sleep_ms

class flowSw:
    def __init__(self, sampleInterval = 5000): #was 10000
        self.pumpCmd = 'OFF'
        self.flowOk = True 
        self.err = 0
        self.flowSw = Pin(4, Pin.IN, Pin.PULL_UP) #Still to Check
        asyncio.create_task(self._run(sampleInterval))

    async def _run(self, sampleInterval):
        _flowSw = False
        while True:
            if self.pumpCmd == 'ON':
                if not _flowSw:
                    self.err = 1 #Waiting flowing on headTk
                await asyncio.sleep_ms(sampleInterval) #Delay time to check
                _flowSw = self.flowSw.value()
                if _flowSw: 
                    self.flowOk = True
                    self.err = 0
                elif not _flowSw:
                    self.flowOk = False
            else:
                if not _flowSw:
                    self.err = 0
                await asyncio.sleep_ms(sampleInterval) #Delay time to check
                _flowSw = self.flowSw.value()
                if _flowSw: 
                    self.flowOk = False
                    self.err = 2 #Flow sensor fault
                elif not _flowSw:
                    self.flowOk = True


            #print("Flow Switch = " + str(_flowSw))
            #print("Flow ok = " + str(self.flowOk) + "   Error = " + str(self.err))


# For tests       
#flowSwTest = flowSw('ON')
#asyncio.run(flowSwTest._run(1000))


#asyncio.create_task(self._run())



        