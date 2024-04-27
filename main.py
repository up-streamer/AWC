import gc
import asyncio
from Connect_WIFI import do_connect
from microdot import Microdot, send_file

pumpMode = 'Auto'
pump = 'OFF'
level = 50
gndtklevel = 75

def main():
    do_connect()
    
    app = Microdot()
        
    gc.collect()
    
    @app.route('/GUI/<path:path>')
    async def static(request, path):
        if '..' in path:
        # directory traversal is not allowed
            return 'Not found', 404
        return send_file('GUI/' + path, max_age=86400)
    
    @app.route('/getControls')
    async def getC(request):
        #global pump
        #global pumpMode
        return {"pump": pump, "pumpMode": pumpMode, "level": level, "gndtklevel":gndtklevel}
    
    # OLD return sample {"timeOfReading":"08\/06\/2017 16:31:38", "level":"500", 
    # "pump": "false", "pumpMode":"true", "gndtklevel":"2500","errorCode":"0"}
    
    @app.route('/updateControls')
    async def updateC(request):
        global pump
        global pumpMode
        requestArgs = request.args
        pumpMode = requestArgs['PumpMode']
        pump = requestArgs['Pump']
        print(" the pump mode is..." + pumpMode)
        print("and pump is... " + pump)
        print(requestArgs)
        return "Success!"

    @app.route('/shutdown')
    async def shutdown(request):
        request.app.shutdown()
        return 'The server is shutting down...'

    app.run(debug=True)

main()