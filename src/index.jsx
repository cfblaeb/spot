import 'chartjs-adapter-date-fns'
import './App.css'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  registerables,
} from 'chart.js'
import StreamingPlugin from '@aziham/chartjs-plugin-streaming'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ChartJS.register(...registerables, StreamingPlugin)

let app_ref = React.createRef()
let feedSocket = new WebSocket('ws://' + window.location.host + '/feed')
let settingsSocket = new WebSocket('ws://' + window.location.host + '/ws_settings')

settingsSocket.onmessage = (e) => {
  const data = JSON.parse(e.data)
  // ...existing code...
  const rootElem = document.getElementById('root');
  if (!window._reactRoot) {
    window._reactRoot = ReactDOM.createRoot(rootElem);
  }
  window._reactRoot.render(
    <App
      ref={app_ref}
      settingsSocket={settingsSocket}
      datastreams_meta={data['streams']}
      seconds_between_updating_live_stream={parseInt(data['seconds_between_updating_live_stream'])}
      seconds_between_storing_measurements={parseInt(data['seconds_between_storing_measurements'])}
    />
  );
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
