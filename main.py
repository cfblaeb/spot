from sanic import Sanic, response
from json import dumps, loads, load, dump
from asyncio import sleep as asleep
from time import time
from datetime import datetime
from io import BytesIO
import bme680
import pandas as pd
skip_bme = False

if not skip_bme:
    sensor = bme680.BME680()
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
app = Sanic()
measurement = {}

app.static('/favicon.ico', './favicon.ico')
app.static('/bundle.js', './dist/bundle.js')
app.static('/', './index.html')

with open('status.json', 'r') as f:
    status = load(f)

# {
#   "polling_delay": 0.01,s
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
        if skip_bme or sensor.get_sensor_data():
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
        dump(status, f)
    await ws.send(dumps(status))


@app.websocket('/ws_settings')
async def new_settings(request, ws):
    await ws.send(dumps(status))
    async for message in ws:
        await consumer(message, ws)


@app.route('/historic_json/<what>/<start>/<end>')
async def historic_json(request, what, start, end):
    with open('data.log') as logfile:
        df = pd.DataFrame([loads(line) for line in logfile])
    df['date'] = pd.to_datetime(df['date'])
    if what in df.columns:
        df = df[['date', what]]
        df = df[(df['date'] > datetime.fromisoformat(start)) & (df['date'] < datetime.fromisoformat(end))]
        df.columns = ['x', 'y']
        return response.json(df.to_json(orient='records'))
    else:
        return response.json(dumps({'error':f'no such things as {what}'}))


@app.route('/pop_data')
async def pop_data(request):
    with open('data.log') as logfile:
        df = pd.DataFrame([loads(line) for line in logfile])
    df['date'] = pd.to_datetime(df['date'])
    return_response = {}

    for key, item in status['streams'].items():
        before_time = time() - int(item["x_axis_seconds"])
        frame = df[df['ts'] > before_time].copy()
        frame = frame[['date', key]]
        frame.columns = ['x', 'y']
        return_response[key] = loads(frame.to_json(orient='records'))
    return response.json(dumps(return_response))


@app.route('all_data')
async def download_all_data(request):
    return await response.file('data.log', filename='data.log')
    ## hmm..data log is in a weird non standard format
    #the following code is kinda slow but converts it to an excel file.
    with open('data.log') as logfile:
        df = pd.DataFrame([loads(line) for line in logfile])
    df['date'] = pd.to_datetime(df['date'])
    # gonna write an excel file to memory
    bio = BytesIO()
    writer = pd.ExcelWriter(bio, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    bio.seek(0)
    return response.raw(bio.read())


@app.route('/<what>_<start>_<end>.xlsx')
async def download_some_data(request, what, start, end):
    with open('data.log') as logfile:
        df = pd.DataFrame([loads(line) for line in logfile])
    df['date'] = pd.to_datetime(df['date'])
    if what in df.columns:
        df = df[['date', what]]
        df = df[(df['date'] > datetime.fromisoformat(start)) & (df['date'] < datetime.fromisoformat(end))]

        # gonna write an excel file to memory
        bio = BytesIO()
        writer = pd.ExcelWriter(bio, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        bio.seek(0)
        return response.raw(bio.read())
    else:
        return response.text("some sort of error...i'm too lazy to code this. Post an issue on github.")


async def polling():
    global measurement
    while True:
        await asleep(int(status['polling_delay']))
        if skip_bme:
            measurement = {
                'temperature': 15,
                'pressure': 1000,
                'humidity': 20,
                'gas': 100,
                'ts': time(),
                'date': str(datetime.now())
            }
            with open('data.log', 'a') as logfile:
                logfile.write(dumps(measurement))
                logfile.write("\n")
        elif sensor.get_sensor_data() and sensor.data.heat_stable:
            measurement = {
                'temperature': sensor.data.temperature,
                'pressure': sensor.data.pressure,
                'humidity': sensor.data.humidity,
                'gas': sensor.data.gas_resistance,
                'ts': time(),
                'date': str(datetime.now())
                }
            with open('data.log', 'a') as logfile:
                logfile.write(dumps(measurement))
                logfile.write("\n")

app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
