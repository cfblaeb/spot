from sanic import Sanic
from json import dumps, loads
from asyncio import sleep as asleep
from time import time
from datetime import datetime
import bme680

#sensor = bme680.BME680()
app = Sanic()
measurement = {}

app.static('/favicon.ico', './dist/favicon.ico')
app.static('/spot.js', './dist/spot.js')
app.static('/', './dist/index.html')

with open('status.json', 'r') as f:
    status = loads(f.read())
#{
# "polling-delay": 0.01,
# "transmit-delay": 1,
# "streams": {"temperature": {"color": "red", "plot_x": 0, "plot_y": 0, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": 10, "y_axis_label": "celcius", "y_axis_from": -50, "y_axis_to": 50, "visible": true},
# "pressure": {"color": "green", "plot_x": 0, "plot_y": 250, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": "10", "y_axis_label": "ehm..pressure..unit", "y_axis_from": 800, "y_axis_to": 1200, "visible": true},
# "humidity": {"color": "blue", "plot_x": 0, "plot_y": 500, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": 10, "y_axis_label": "% humidity", "y_axis_from": 0, "y_axis_to": 100, "visible": true}}
# }

status['server-time'] = time()

@app.websocket('/feed')
async def feed(request, ws):
    await ws.send(dumps(status))
    while True:
        await asleep(status['transmit-delay'])
        if True:#sensor.get_sensor_data():
            await ws.send(dumps(measurement))
# Some sort of code to recieve status updates


async def polling():
    global measurement
    last_time = time()
    while True:
        await asleep(status['polling-delay'])
        if True:#sensor.get_sensor_data():
            measurement = {
                'temperature': 10,#sensor.data.temperature, 
                'pressure': 1000, #sensor.data.pressure, 
                'humidity':50, #sensor.data.dddd, 
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