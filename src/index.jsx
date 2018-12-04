// @flow
import './App.css'
import 'chartjs-plugin-streaming'
import React from 'react'
import ReactDOM from 'react-dom'
import App from './App.jsx'

let app_ref: {current: null | App} = React.createRef()
let feedSocket = new WebSocket('ws://' + window.location.host + '/feed')
let settingsSocket = new WebSocket('ws://' + window.location.host + '/ws_settings')

settingsSocket.onmessage = (e) => {
	const data = JSON.parse(e.data)
	//{"seconds_between_updating_live_stream": "1", "seconds_between_storing_measurements": "60",
	// "streams": {
	//   "temperature": {"color": "#FF0000","plot_width": 1000,"plot_height": 200,"x_axis_seconds": "30","y_axis_label": "celcius"},
	//   "pressure": {
	//   "humidity": {
	//   "gas":
	ReactDOM.render(
		<App
			ref={app_ref}
			settingsSocket={settingsSocket}
			datastreams_meta={data['streams']}
			seconds_between_updating_live_stream={parseInt(data['seconds_between_updating_live_stream'])}
			seconds_between_storing_measurements={parseInt(data['seconds_between_storing_measurements'])}
		/>,
		document.getElementById('root'))
}

settingsSocket.onclose = function () {
	console.error('settingsSocket closed unexpectedly')
}

feedSocket.onmessage = (e) => {
	if (typeof e.data === 'string' || e.data instanceof String) {
		const data = JSON.parse(e.data)
		if (app_ref.current != null) {
			app_ref.current.newServerData(data)
		}
	}
}

feedSocket.onclose = function () {
	console.error('feedSocket closed unexpectedly')
}
