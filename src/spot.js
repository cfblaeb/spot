import Chart from 'chart.js'
import './style.css'

var datastreams = {} // list of plots
var server_client_time_offset = 'NOTSET'
var chatSocket = new WebSocket('ws://' + window.location.host + '/feed')

function x_axis_seconds_controller_updater(event) {
	let key = event.target.getAttribute('data-key')
	//datastreams[key].chart
	console.log(event)
	console.log(datastreams[key].x_axis_seconds)
	datastreams[key].x_axis_seconds = event.target.value*1000
	console.log(datastreams[key].x_axis_seconds)
}

chatSocket.onmessage = function (e) {
	let data = JSON.parse(e.data)
	if ('server-time' in data) { // first message
		server_client_time_offset = Date.now() - data['server-time'] * 1000
		/* name of stream: {
			"color": "red",
			"plot_x": 0, "plot_y": 0,
			"plot_width": 1000, "plot_height": 200,
			"x_axis_label": "seconds", "x_axis_seconds": 10,
			"y_axis_label": "celcius",
			"y_axis_from": -50, "y_axis_to": 50,
			"visible": true},
		*/
		for (const [key, value] of Object.entries(data['streams'])) {
			let x_axis_seconds_controller = document.createElement('input')
			x_axis_seconds_controller.type = 'number'
			x_axis_seconds_controller.min = 1
			x_axis_seconds_controller.value = 10
			x_axis_seconds_controller.setAttribute('data-key', key)
			x_axis_seconds_controller.onchange=x_axis_seconds_controller_updater
			//<input type="number" name="quantity" min="1" max="5">
			document.body.appendChild(x_axis_seconds_controller)
			let container = document.createElement('div')
			container.className = 'chart-container'
			let tc = document.createElement('canvas')
			tc.id = key + '_canvas'
			tc.width = value['plot_width']
			tc.height = value['plot_height']
			tc.style.border = '1px solid'
			container.appendChild(tc)
			document.body.appendChild(container)
			let scatterChart = new Chart(tc.getContext('2d'), {
				type: 'scatter',
				data: {
					datasets: [{
						label: key,
						data: [],
						//fill: false,
						borderColor: value['color'],
					}]
				},
				options: {
					maintainAspectRatio: false,
					animation: {easing: 'linear',duration: 100,},
					hover: {animationDuration: 0,},
					responsiveAnimationDuration: 0, showLines: true, elements: {line: { tension: 0}},
					scales: {
						xAxes: [{
							type: 'time',
							position: 'bottom',
							ticks: {/*minRotation: 90, source: 'labels'*/}, 
							time: {min: Date.now()-value['x_axis_seconds']*1000, max: Date.now()}}]}
				}
			})
			datastreams[key] = {chart: scatterChart, x_axis_seconds: value['x_axis_seconds']*1000}
		}
	}
	else {
		for (const key of Object.keys(datastreams)) {
			/* {
					temperature: 10,
					pressure: 1000,
					humidity: 50,
					ts: 1539532247.161099,
					date: "2018-10-14 17:50:47.161103"
				}
			*/
			datastreams[key].chart.data.datasets[0].data.push(
				{
					t: data['ts'] * 1000 + server_client_time_offset,
					y: data[key]
				})
			datastreams[key].chart.data.datasets[0].data = datastreams[key].chart.data.datasets[0].data.filter(el => el.t > (Date.now()-datastreams[key].x_axis_seconds))
			datastreams[key].chart.options.scales.xAxes[0].time.min = Date.now()-datastreams[key].x_axis_seconds
			datastreams[key].chart.options.scales.xAxes[0].time.max = Date.now()

			datastreams[key].chart.update()
		}
	}
}

chatSocket.onclose = function () {
	console.error('Websocket closed unexpectedly')
}
