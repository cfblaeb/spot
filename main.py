from sanic import Sanic
from json import dumps
from asyncio import sleep as asleep
from time import time
from datetime import datetime
import bme680

sensor = bme680.BME680()
measurements = []
app = Sanic()

app.static('/', './html/index.html')
app.static('/spot.js', './js/spot.js')

@app.websocket('/feed')
async def feed(request, ws):
    while True:
        await asleep(0.1)
        await ws.send(dumps(measurements[-1]))

async def polling():
    global measurements
    while True:
        await asleep(0.01)
        if sensor.get_sensor_data():
            meas = {'temperature':sensor.data.temperature, 'pressure':sensor.data.pressure, 'humidity':sensor.data.humidity, 'ts':time(), 'date': datetime.now()}
            if len(measurements) > 10000:
                #write to file and empty
                #then remove all old values
                measurements = [meas]
            else:
                measurements.append(meas)


app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)