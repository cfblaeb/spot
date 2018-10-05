from sanic import Sanic
from sanic.response import json
from asyncio import sleep as asleep
from random import randint

measurements = []
app = Sanic()

app.static('/', './html/index.html')

@app.websocket('/feed')
async def feed(request, ws):
    while True:
        await asleep(0.1)
        await ws.send(str(measurements[-1]))

async def polling():
    global measurements
    while True:
        await asleep(0.01)
        if len(measurements) != 0:
            nn = measurements[-1]+randint(0, 10)-5
        else:
            nn = 50
        if nn > 100:
            nn = 100
        elif nn < 0:
            nn = 0
        if len(measurements) > 10000:
            #write to file and empty
            #then remove all old values
            measurements = [measurements[-1]]
        measurements.append(nn)


app.add_task(polling())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)