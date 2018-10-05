var canvas_size = [1000,150] // this isnt actually free to be set...its not incorporated in calculations everywhere the info is used
var width_buffer = 10
var grid_divider_vertical = 20

class datapoint {
	constructor(y, timepoint) {
		this.x = canvas_size[0]
		this.y = y
		this.mytime = timepoint
	}
}

// settings
var data_streams = { // min,max
	temperature:[-20, 50, null, []], 
	pressure:[800, 1200, null, []],
	humidity:[0, 100, null, []]
}

var server_client_time_offset = "NOTSET"

for (let key of Object.keys(data_streams)) {
	let tc = document.createElement("canvas")
	tc.id = key
	tc.width = canvas_size[0]-width_buffer
	tc.height = canvas_size[1]
	tc.style.border = "1px solid"
	document.body.appendChild(tc)
	data_streams[key][2] = tc
}

var chatSocket = new WebSocket("ws://" + window.location.host + "/feed")

chatSocket.onmessage = function(e) {
	let data = JSON.parse(e.data)
	if (server_client_time_offset === "NOTSET") {
		server_client_time_offset = Date.now()-data["ts"]*1000
	}
	for (let key of Object.keys(data_streams)) {
		data_streams[key][3].push(new datapoint(data[key], data["ts"]*1000-server_client_time_offset))
	}
}

chatSocket.onclose = function() {
	console.error("Websocket closed unexpectedly")
}

function draw() {
	for (let key of Object.keys(data_streams)) {
		let ctx = data_streams[key][2].getContext("2d")
		data_streams[key][3] = data_streams[key][3].filter(
			el => el.x>0).map(el => {el.x=canvas_size[0]-(Date.now()-el.mytime)/10;return el})
		ctx.clearRect(0, 0, canvas_size[0]-width_buffer, canvas_size[1])
		//vertical
		Array.from(Array(11).keys()) .forEach((el) => {
			ctx.fillText(el, 997.5-(el*100), canvas_size[1])
			ctx.fillRect(canvas_size[0]-(el*100), 0, 1,140)
		})
		//horizontal
		let scale_width = data_streams[key][1]-data_streams[key][0]
		Array.from(Array(Math.round(canvas_size[1]/grid_divider_vertical)).keys()) .forEach((el) => {
			ctx.fillText(
				((canvas_size[1]-el*grid_divider_vertical)/canvas_size[1])*scale_width+data_streams[key][0], 
				canvas_size[0]-50, el*grid_divider_vertical
			)
			ctx.fillRect(0, el*grid_divider_vertical, canvas_size[0], 1)
		})
		ctx.fillStyle = "rgb(255,4,255)"
		
		
		data_streams[key][3].forEach(el=>ctx.fillRect(el.x, canvas_size[1]-((el.y-data_streams[key][0])/scale_width)*canvas_size[1], 5, 5))
	}
    
	//request more frames
	window.requestAnimationFrame(draw)
}

window.requestAnimationFrame(draw)