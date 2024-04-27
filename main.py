import gc
import asyncio
from Connect_WIFI import do_connect
from microdot import Microdot, send_file
from uP_AJ_SR04 import AJ_SR04, Measurements
from pump_control import PumpControl
from messages import texts

Data = {
    "pump":'OFF',
    "pumpMode":'Auto',   
    "pumpStatus":'Ok',
    "headTklevel":50,
    "headTkVol":1234,
    "headTkStatus":'Ok',
    "gndTkLevel":75,
    "gndTkVol":4321,
    "gndTkStatus":'Ok',
    }

async def main():
    Sensor = AJ_SR04()
    
    await Sensor
    
    Pump = PumpControl(10, 90) # min and max percent limits
    
    do_connect()
    
    app = Microdot()
    
    msg = texts()
    
    gc.collect()
    
    @app.route('/GUI/<path:path>')
    async def static(request, path):
        if '..' in path:
        # directory traversal is not allowed
            return 'Not found', 404
        return send_file('GUI/' + path, max_age=86400)
    
    @app.route('/getControls')
    async def getC(request):
        return Data
    
    # OLD return sample {"timeOfReading":"08\/06\/2017 16:31:38", "level":"500", 
    # "pump": "false", "pumpMode":"true", "gndtklevel":"2500","errorCode":"0"}
    
    @app.route('/updateControls')
    async def updateC(request):
        requestArgs = request.args
        Data["pumpMode"] = requestArgs['PumpMode']
        Data["pump"] = requestArgs['Pump']
        print(" the pump mode is..." + Data["pumpMode"])
        print("and pump is... " + Data["pump"])
        print(requestArgs)
        return "Success!"

    @app.route('/shutdown')
    async def shutdown(request):
        request.app.shutdown()
        return 'The server is shutting down...'
    
    
    async def sincData(): # Sincronize/transfer all data co-routines
        while True:
            print("Percentage = " + Sensor.measurements.percentage + " %")
            #print("Volume = " + Sensor.measurements.volume + " Lts")
            #print("Tank Level = " + str(Sensor.measurements.level) + " mm")
            print("Tank Error Code = " + str(Sensor.err))
            print("")
            Data["headTklevel"] = Sensor.measurements.percentage
            Data["headTkVol"] = Sensor.measurements.volume
            Pump.percentageLevel = Data["headTklevel"]
            Pump.mode = Data["pumpMode"]
            if Pump.mode == 'Auto':    # Pump command direction
                Data["pump"] = Pump.pumpCommand
            else:
                Pump.pumpCommand = Data["pump"]
            Pump.sensorError = Sensor.err
            
            Data["pumpStatus"] = msg.pumpMsg[Pump.err]
            Data["headTkStatus"] = msg.sensorMsg[Sensor.err]

            await asyncio.sleep_ms(1000)

    asyncio.create_task(sincData())
    app.run(debug=True)      
         
asyncio.run(main())


