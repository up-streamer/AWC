import gc
import asyncio
from Connect_WIFI import do_connect
from microdot import Microdot, send_file
from uP_AJ_SR04 import AJ_SR04, Measurements
from pump_control import PumpControl
from flow_switch import flowSw
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
    "flowSrStatus":'Ok',
    }

async def main():
    headTk = AJ_SR04(COM = 2, sampleInterval = 1000)
    headTk.max_distance = 974
    headTk.min_distance = 250
    headTk.max_volume = 1000
    await headTk
    
    groundTk = AJ_SR04(COM = 1, sampleInterval = 5000)
    groundTk.max_distance = 974
    groundTk.min_distance = 250
    groundTk.max_volume = 10000
    await groundTk

    Pump = PumpControl(10, 90) # min and max percent limits

    Water = flowSw()

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
            print("Percentage = " + headTk.measurements.percentage + " %")
            #print("Volume = " + headTk.measurements.volume + " Lts")
            #print("Tank Level = " + str(headTk.measurements.level) + " mm")
            print("Tank Error Code = " + str(headTk.err))
            print("")
            Data["gndTkLevel"] = groundTk.measurements.percentage
            Data["gndTkVol"] = groundTk.measurements.volume
            Data["headTklevel"] = headTk.measurements.percentage
            Data["headTkVol"] = headTk.measurements.volume
            Pump.headTklevel = Data["headTklevel"]
            Pump.mode = Data["pumpMode"]

            if Pump.mode == 'Completar' and Data["pump"] == 'ON': #Fill Up command
                Pump.pumpCommand = Data["pump"]
                Data["pumpMode"] = 'Auto'
          
            if Pump.mode == 'Auto':    # Pump command direction
                Data["pump"] = Pump.pumpCommand
            else:
                Pump.pumpCommand = Data["pump"]

            Water.pumpCmd = Pump.pumpCommand
            Pump.headTkErr = headTk.err
            Pump.flowOk = Water.flowOk

            Data["pumpStatus"] = msg.pumpMsg[Pump.err]
            Data["headTkStatus"] = msg.tankMsg[headTk.err]
            Data["gndTkStatus"] = msg.tankMsg[groundTk.err]
            Data["flowSrStatus"] = msg.flowMsg[Water.err]
            print("Pump Status = " + msg.pumpMsg[Pump.err])
            await asyncio.sleep_ms(1000)

    asyncio.create_task(sincData())
    app.run(debug=True)      

asyncio.run(main())


