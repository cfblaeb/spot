from sanic import Sanic
from sanic.response import json, file, raw, text
from json import dumps, loads, load, dump
from asyncio import sleep as asleep
from time import time
from datetime import datetime
from io import BytesIO
import bme680
import pandas as pd

# MIMIC SENSOR DATA.
# Set to False to use real sensor data,
# True to use fake data.
# Use during dev without actual access to the BME680 chip.
skip_bme = False

if not skip_bme:
    sensor = bme680.BME680()
    # Ensure ambient_temperature is set before calculating heater resistance
    if sensor.ambient_temperature is None:
        sensor.get_sensor_data()
    if sensor.ambient_temperature is None:
        sensor.ambient_temperature = 25  # Fallback to a default if still None

    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

app = Sanic("zeroSPOT")
measurement = {}

app.static('/favicon.ico', './favicon.ico', name='favicon')
app.static('/bundle.js', './dist/bundle.js', name='bundle')
app.static('/', './index.html', name='index')

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
    async for message in ws:
        await consumer(message, ws)


@app.route('/historic_json/<what>/<start>/<end>')
async def historic_json(request, what, start, end):
    try:
        with open('data.log') as logfile:
            data = []
            for line in logfile:
                line = line.replace('\x00', '').strip()
                if line:
                    try:
                        data.append(loads(line))
                    except ValueError:
                        continue
            df = pd.DataFrame(data)
    except FileNotFoundError:
        return json({'error': 'data.log not found'})

    if df.empty:
        return json([])

    df['date'] = pd.to_datetime(df['date'])
    if what in df.columns:
        df = df[['date', what]]
        df = df[(df['date'] > datetime.fromisoformat(start)) & (df['date'] < datetime.fromisoformat(end))]
        df.columns = ['x', 'y']
        return json(df.to_json(orient='records'))
    else:
        return json({'error':f'no such things as {what}'})


@app.route('all_data')
async def download_all_data(request):
    return await file('data.log', filename='data.log')
    # The following code converts to Excel file in memory
    try:
        with open('data.log') as logfile:
            data = []
            for line in logfile:
                line = line.replace('\x00', '').strip()
                if line:
                    try:
                        data.append(loads(line))
                    except ValueError:
                        continue
            df = pd.DataFrame(data)
    except FileNotFoundError:
        return text("data.log not found")

    if df.empty:
        return text("No data available")

    df['date'] = pd.to_datetime(df['date'])
    bio = BytesIO()
    writer = pd.ExcelWriter(bio, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()
    bio.seek(0)
    return raw(bio.read())


@app.route('/<name:ext=xlsx>')
async def download_some_data(request, name, ext):
    try:
        what, start, end = name.split("_")
    except ValueError:
        return text("Invalid filename format. Expected what_start_end.xlsx")
    print(name, ext)
    print(what, start, end)
    try:
        with open('data.log') as logfile:
            data = []
            for line in logfile:
                line = line.replace('\x00', '').strip()
                if line:
                    try:
                        data.append(loads(line))
                    except ValueError:
                        continue
            df = pd.DataFrame(data)
    except FileNotFoundError:
        return text("data.log not found")

    if df.empty:
        return text("No data available")

    df['date'] = pd.to_datetime(df['date'])
    if what in df.columns:
        df = df[['date', what]]
        df = df[(df['date'] > datetime.fromisoformat(start)) & (df['date'] < datetime.fromisoformat(end))]
        bio = BytesIO()
        writer = pd.ExcelWriter(bio, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.close()
        bio.seek(0)
        return raw(bio.read())
    else:
        return text("some sort of error...i'm too lazy to code this. Post an issue on github.")


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
    else:
        try:
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                measurement = {
                    'temperature': sensor.data.temperature,
                    'pressure': sensor.data.pressure,
                    'humidity': sensor.data.humidity,
                    'gas': sensor.data.gas_resistance,
                    'ts': time(),
                    'date': str(datetime.now())
                }
            else:
                print("Sensor data not ready or heat not stable")
        except Exception as e:
            print(f"Error performing measurement: {e}")


async def polling():
    # Ensure data.log exists
    try:
        open('data.log', 'x').close()
    except FileExistsError:
        pass
    while True:
        wait_time = int(status['seconds_between_storing_measurements'])
        await asleep(wait_time)
        # check if current measurement is "new enough", and if so, just use it
        new_enough = wait_time/10  # new enough is 1/10th of wait time
        if "ts" not in measurement or measurement['ts']+new_enough < time():
            await perform_measurement()
        if measurement:
            with open('data.log', 'a') as logfile:
                logfile.write(dumps(measurement))
                logfile.write("\n")


app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
