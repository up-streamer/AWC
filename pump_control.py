import asyncio
from machine import Pin
from time import sleep_ms

class PumpControl:
    def __init__(self, startPerct, stopPerct, sampleInterval = 1000):
        self.startPerct = startPerct
        self.stopPerct = stopPerct
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
        
    async def _run(self, sampleInterval):
        while True:
            percentage = float(self.percentageLevel)
            err = self.err + self.sensorError
            
            if self.mode == 'Auto':
                if err == 0:
                    if percentage <= self.startPerct:
                        self.pump.on()
                        self.pumpCommand = 'ON'
                    elif(percentage >= self.stopPerct):
                        self.pump.off()
                        self.pumpCommand = 'OFF'
                else:
                    self.pump.off()
                    self.pumpCommand = 'OFF'
                    if self.err == 2:
                        self.err = 0 # Reset Caution message

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
                
        