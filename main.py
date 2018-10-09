from sanic import Sanic
from json import dumps
from asyncio import sleep as asleep
from time import time
from datetime import datetime
import bme680

#sensor = bme680.BME680()
app = Sanic()
measurement = {}

app.static('/', './html/index.html')
app.static('/spot.js', './js/spot.js')
app.static('/favicon.ico', './img/favicon.ico')

@app.websocket('/feed')
async def feed(request, ws):
    while True:
        await asleep(0.05)
        if True:#sensor.get_sensor_data():
            await ws.send(dumps(measurement))

async def polling():
    global measurement
    last_time = time()
    while True:
        await asleep(0.01)
        if True:#sensor.get_sensor_data():
            measurement = {
                'temperature': 10,#sensor.data.temperature, 
                'pressure': 1000, #sensor.data.pressure, 
                'humidity':50, #sensor.data.humidity, 
                'ts':time(), 
                'date': str(datetime.now())
                }
            ctime = time()
            if ctime-last_time>60: # log once every 60 seconds
                with open('data.log', 'a') as logfile:
                    logfile.write(dumps(measurement))
                    logfile.write("\n")
                last_time = ctime

app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)