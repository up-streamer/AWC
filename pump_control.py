import asyncio
from machine import Pin
from time import sleep_ms

class PumpControl:
    def __init__(self, startPerct, stopPerct, sampleInterval = 1000):
        self.startPerct = startPerct
        self.stopPerct = stopPerct
        self.flowOk = True 
        self.mode = 'Auto'
        self.pumpCommand = 'OFF'
        self.percentageLevel = 0
        self.sensorError = 0
        self.err = 0
        self.pump = Pin(2, Pin.OUT)
        self.pump.off()
        if startPerct >= stopPerct:            
            self.err = 1           #Setup limits inverted
        asyncio.create_task(self._run(sampleInterval))

    def _retry(self, sampleInterval):
        self.err = 3 #Retry
        for attempt in range(3):
            print("----> RETRY! attempt = " + str(attempt))
            for delay in range (10): #Was 15
                if self.mode == 'Auto' and not self.sensorError:
                    await asyncio.sleep_ms(sampleInterval)
                    print("delay OFF = " + str(delay))
                else:
                    self.pump.off()
                    self.pumpCommand = 'OFF'
                    return 

            self.pump.on()
            self.pumpCommand = 'ON'

            for delay in range (10):  #Was 30
                if self.mode == 'Auto' and not self.sensorError:
                    print("delay ON = " + str(delay))
                    await asyncio.sleep_ms(sampleInterval)
                else:
                    self.pump.off()
                    self.pumpCommand = 'OFF'
                    return
                
            if self.flowOk:
                self.err = 0
                return    # Stop retries
            else:
                self.pump.off()
                self.pumpCommand = 'OFF'
                
#         if self.sensorError:
#             self.err = 4
#         else:
#             self.err = 5 #Time out no flow
        self.err = 5 #Time out no flow
        self.pump.off()
        self.pumpCommand = 'OFF'
        return

    async def _run(self, sampleInterval):
        while True:
            percentage = float(self.percentageLevel)
            err = self.err + self.sensorError

            if self.mode == 'Auto':
                if err == 0  and self.flowOk == True:
                    if percentage <= self.startPerct:
                        self.pump.on()
                        self.pumpCommand = 'ON'
                    elif(percentage >= self.stopPerct):
                        self.pump.off()
                        self.pumpCommand = 'OFF'
                else:
                    self.pump.off()
                    self.pumpCommand = 'OFF'
                    print("-----> Flow ok from pump_control = " + str(self.flowOk))

                    if self.err == 2:
                        self.err = 0 # Reset Caution message
                        
                    if self.sensorError:
                        self.err = 4
                        
                    if self.err < 4: #Time out no flow
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
