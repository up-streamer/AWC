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
    connection = await do_connect()

    app = Microdot()

    headTk = AJ_SR04(COM = 2, sampleInterval = 1000)
    headTk.max_distance = 974
    headTk.min_distance = 250
    headTk.max_volume = 1000
    headTk.start()
    await headTk
    groundTk = AJ_SR04(COM = 1, sampleInterval = 5000)
    groundTk.max_distance = 974
    groundTk.min_distance = 250
    groundTk.max_volume = 10000
    groundTk.start()
    await groundTk

    Water = flowSw()
    Water.start()

    Pump = PumpControl()
    Pump.startPerct = 10 # min and max percent limits
    Pump.stopPerct = 90
    Pump.start() ### Try for compatibility

    msg = texts()

    @app.route('/GUI/<path:path>')
    async def static(request, path):
        if '..' in path:
        # directory traversal is not allowed
            return 'Not found', 404
        return send_file('GUI/' + path, max_age=86400)

    @app.route('/getControls')
    async def getC(request):
        Data["gndTkLevel"] = groundTk.measurements.percentage
        Data["gndTkVol"] = groundTk.measurements.volume
        Data["headTklevel"] = headTk.measurements.percentage
        Data["headTkVol"] = headTk.measurements.volume

        Data["headTkStatus"] = msg.tankMsg[headTk.err]
        Data["gndTkStatus"] = msg.tankMsg[groundTk.err]
        Data["flowSrStatus"] = msg.flowMsg[Water.err]
        Data["pumpStatus"] = msg.pumpMsg[Pump.err]

        Data["pump"] = Pump.pumpCommand
        Data["pumpMode"] = Pump.mode

        return Data

    @app.route('/updateControls')
    async def updateC(request):
        requestArgs = request.args
        Pump.mode = Data["pumpMode"] = requestArgs['PumpMode']
        Data["pump"] = requestArgs['Pump']
        
        if (Pump.mode == 'Manual') or (Pump.mode == 'Completar'):
            Pump.pumpCommand = Data["pump"]

        print(requestArgs)
        return "Success!"
    
    # To be implemented on GUI and test
    @app.route('/shutdown')
    async def shutdown(request):
        request.app.shutdown()
        return 'The server is shutting down...'

    async def sincData(): # Sincronize/transfer all data co-routines
        while True:
            Pump.headTkLevel = headTk.measurements.percentage
            Water.pumpCmd = Pump.pumpCommand
            Pump.headTkErr = headTk.err
            Pump.flowOk = Water.err

            await asyncio.sleep_ms(500)

    async def reconnect():
        while True:
            await asyncio.sleep(30)
            if not connection.isconnected():
                print("Connecting...")
                await do_connect()

    asyncio.create_task(reconnect())

    asyncio.create_task(sincData())

    gc.collect()

    app.run(debug=True)

asyncio.run(main())
