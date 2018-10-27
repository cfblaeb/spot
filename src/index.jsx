// @flow
import './App.css'
import 'chartjs-plugin-streaming'
import React from 'react'
import ReactDOM from 'react-dom'
import App from './App.jsx'

var app_ref: {current: null | App} = React.createRef()
var feedSocket = new WebSocket('ws://' + window.location.host + '/feed')
var settingsSocket = new WebSocket('ws://' + window.location.host + '/ws_settings')

settingsSocket.onmessage = (e: any) => {
	const data = JSON.parse(e.data)
	//{ "polling_delay": 0.01, "transmit_delay": 0.5, "streams": {
	//		"temperature": {"color": "red", "plot_x": 0, "plot_y": 0, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": 10, "y_axis_label": "celcius", "y_axis_from": -50, "y_axis_to": 50, "visible": true},
	//		"pressure": {"color": "green", "plot_x": 0, "plot_y": 250, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": "10", "y_axis_label": "ehm..pressure..unit", "y_axis_from": 800, "y_axis_to": 1200, "visible": true},
	//		"humidity": {"color": "blue", "plot_x": 0, "plot_y": 500, "plot_width": 1000, "plot_height": 200, "x_axis_label": "seconds", "x_axis_seconds": 10, "y_axis_label": "% humidity", "y_axis_from": 0, "y_axis_to": 100, "visible": true}}}*/

	//server_hardware_polling_frequency: data['polling_delay'],
	ReactDOM.render(
		<App
			ref={app_ref}
			settingsSocket={settingsSocket}
			datastreams_meta={data['streams']}
			server_transmit_frequency={parseInt(data['transmit_delay'])}
		/>,
		document.getElementById('root'))
}

feedSocket.onmessage = (e) => {
	const data = JSON.parse(e.data)
	if (app_ref.current != null) {
		app_ref.current.newServerData(data)
	}
}

feedSocket.onclose = function () {
	console.error('feedSocket closed unexpectedly')
}
settingsSocket.onclose = function () {
	console.error('settingsSocket closed unexpectedly')
}
