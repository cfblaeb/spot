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
I'm gonna code a little simple python webserver using [sanic](https://github.com/huge-success/sanic).  
The server will poll the sensor often and it will occasionally send that data via [websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) to any connected clients
## client-side
The server will serve 1 static html page with a [canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) element per data stream.  
It will connect to the server via [websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) and everytime it gets a datapacket its going to plot it  
The canvas element will feature a time scrolling view of the data