# spot
This is a little fun side project to see how hard/easy it is to make a Temperature, air pressure, humidity and "air quality" logger.

# Hardware
I didn't want to solder anything so I bought:
* 1x Raspberry Pi Zero WH (pre-soldered)
  - This is a full computer with wifi.
* 1x BME680 Breakout - Air Quality, Temperature, Pressure, Humidity Sensor
  - This is a board with a BOSCH chip that does the actual measurements
* 1x Breakout Garden HAT
  - This is a clever little thing that makes it easy to connect "Breakout" boards to a Raspberry.

# Software
## Server-side
To use the bme680 I just used the vendor provided library [bme680](https://github.com/pimoroni/bme680-python)  
I used the never recommendable, but very convenient "curl https://get.pimoroni.com/bme680 | bash" on a clean raspbian install  
Then I installed python 3.7 using [pyenv](https://github.com/pyenv/pyenv)  
and run 'pip install wheel' before 'pip install -r requirements.txt'  

I'm gonna code a little simple python webserver using [sanic](https://github.com/huge-success/sanic).  
The server will poll the sensor often and it will occasionally send that data via [websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) to any connected clients
## client-side
The server will serve 1 static html page with a [canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) element per data stream.  
It will connect to the server via [websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) and everytime it gets a datapacket its going to plot it  
The canvas element will feature a time scrolling view of the data powered by [charts.js] (chartjs.org)

## to do list
* settings
  * calibration offset
  * log file storage place
* realtime (back and front)
  * make it so that realtime is updated more frequently. Separately from logging delay
    * So a log time and a measure/transmit time

## post development thoughts
* hardware
  * impressively easy. No major complaints.
* Software  
  * Is sanic good...I dont know. Yes I guess. I feel like I dont fully understand it.
  * My own code: Combination of learning curve (my first websocket, sanic and chartjs project) and lazyness and time constraints have produced a less than perfect yet functional product. 