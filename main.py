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
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

app = Sanic()
measurement = {}

app.static('/favicon.ico', './favicon.ico')
app.static('/bundle.js', './dist/bundle.js')
app.static('/', './index.html')

with open('status.json', 'r') as f:
    status = load(f)

# {
#   "seconds_between_updating_live_stream": "1",
#   "seconds_between_storing_measurements": "60",
#   "streams": {
#     "temperature": {
#       "color": "#FF0000",
#       "plot_width": 1000,
#       "plot_height": 200,
#       "x_axis_seconds": "30",
#       "y_axis_label": "celcius"
#     },
#     "pressure": {
#       "color": "#00FF00",
#       "plot_width": 1000,
#       "plot_height": 200,
#       "x_axis_seconds": "50",
#       "y_axis_label": "hPa"
#     },
#     "humidity": {
#       "color": "#0000FF",
#       "plot_width": 1000,
#       "plot_height": 200,
#       "x_axis_seconds": "19",
#       "y_axis_label": "% humidity"
#     },
#     "gas": {
#       "color": "#FFA500",
#       "plot_width": 1000,
#       "plot_height": 200,
#       "x_axis_seconds": "10",
#       "y_axis_label": "Ohms"
#     }
#   }
# }


# live feed. Just sends the latest measurement
@app.websocket('/feed')
async def feed(request, ws):
    while True:
        await asleep(int(status['seconds_between_updating_live_stream']))
        await perform_measurement()
        await ws.send(dumps(measurement))


# settings "consumer". It interprets requests to change settings
async def consumer(mesmes, ws):
    # TODO: less naive input handling
    new_data = loads(mesmes)
    if new_data['label'] == 'root':
        status[new_data['key']] = new_data['value']
    else:
        status["streams"][new_data['label']][new_data['key']] = new_data['value']
    with open('status.json', 'w') as f:
        dump(status, f)  # write new status
    await ws.send(dumps(status))


@app.websocket('/ws_settings')
async def new_settings(request, ws):
    await ws.send(dumps(status))  # return new status to server
    async for message in ws:  # consume incomming requests for settings changes
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


async def perform_measurement():
    global measurement
    if skip_bme:
        measurement = {
            'temperature': 15,
            'pressure': 1000,
            'humidity': 20,
            'gas': 100,
            'ts': time(),
            'date': str(datetime.now())
        }
    elif sensor.get_sensor_data() and sensor.data.heat_stable:
        measurement = {
            'temperature': sensor.data.temperature,
            'pressure': sensor.data.pressure,
            'humidity': sensor.data.humidity,
            'gas': sensor.data.gas_resistance,
            'ts': time(),
            'date': str(datetime.now())
        }


async def polling():
    while True:
        wait_time = int(status['seconds_between_storing_measurements'])
        await asleep(wait_time)
        # check if current measurement is "new enough", and if so, just use it
        new_enough = wait_time/10  # new enough is 1/10th of wait time
        if measurement['ts']+new_enough < time():
            await perform_measurement()
        with open('data.log', 'a') as logfile:
            logfile.write(dumps(measurement))
            logfile.write("\n")


app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
