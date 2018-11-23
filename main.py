from sanic import Sanic, response
from json import dumps, loads
from asyncio import sleep as asleep
from time import time
from datetime import datetime
import bme680
import pandas as pd

#sensor = bme680.BME680()
app = Sanic()
measurement = {}

app.static('/favicon.ico', './favicon.ico')
app.static('/bundle.js', './dist/bundle.js')
app.static('/', './index.html')

with open('status.json', 'r') as f:
    status = loads(f.read())

# {
#   "polling_delay": 0.01,
#   "transmit_delay": 1,
#   "streams": {
#       "temperature": {"color": "#FF0000", "plot_width": 1000, "plot_height": 200,
#           "x_axis_seconds": 10, "y_axis_label": "celcius", "y_axis_from": -50, "y_axis_to": 50,
#           "visible": true},
#       "pressure": {"color": "#00FF00", plot_width": 1000, "plot_height": 200, "x_axis_seconds": 10, "y_axis_label": "ehm..pressure..unit", "y_axis_from": 800, "y_axis_to": 1200, "visible": true},
#       "humidity": {"color": "#0000FF", "plot_width": 1000, "plot_height": 200, "x_axis_seconds": 10, "y_axis_label": "% humidity", "y_axis_from": 0, "y_axis_to": 100, "visible": true}
#   }
# }

#status['server-time'] = time()

@app.websocket('/feed')
async def feed(request, ws):
    while True:
        await asleep(int(status['transmit_delay']))
        if True: #sensor.get_sensor_data():
            await ws.send(dumps(measurement))

async def consumer(mesmes, ws):
    new_data = loads(mesmes)
    # remember to sanitize input!!
    if new_data['label'] == 'root':
        if new_data['key'] == 'polling_delay':
            status['polling_delay'] = new_data['value']
            if int(new_data['value']) > int(status['transmit_delay']):
                # transmit_delay >= polling_delay
                status['transmit_delay'] = new_data['value']
        elif new_data['key'] == 'transmit_delay':
            status['transmit_delay'] = new_data['value']
            if int(new_data['value']) < int(status['polling_delay']):
                # polling_delay <= transmit_delay
                status['polling_delay'] = new_data['value']
    else:
        # TODO: sanitize input!!
        status["streams"][new_data['label']][new_data['key']] = new_data['value']
    with open('status.json', 'w') as f:
        f.write(dumps(status))
    await ws.send(dumps(status))

@app.websocket('/ws_settings')
async def new_settings(request, ws):
    await ws.send(dumps(status))
    async for message in ws:
        await consumer(message, ws)

@app.route('/historic_json/<what>/<from>/<to>')
async def historic_json(request, what, from, to):
    with open('data.log') as logfile:
        df = pd.DataFrame([loads(line) for line in logfile])
    df['date'] = pd.to_datetime(df['date'])
    df = df[['date', what]]
    df = df[df[('date'] > datetime.fromisoformat(from)) & (date['date'] < datetime.fromisoformat(to))]
    return response.json(df.to_json(orient='records'))

async def polling():
    global measurement
    while True:
        await asleep(int(status['polling_delay']))
        if True:#sensor.get_sensor_data():
            measurement = {
                'temperature': 25,#sensor.data.temperature,
                'pressure': 1000,#sensor.data.pressure,
                'humidity': 50,#sensor.data.humidity,
                'ts':time(),
                'date': str(datetime.now())
                }
            with open('data.log', 'a') as logfile:
                logfile.write(dumps(measurement))
                logfile.write("\n")

app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
