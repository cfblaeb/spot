// @flow
import React, { Component } from 'react'

type Props = {
	datastreams_meta: {[string]: {[string]: string }},
	server_transmit_frequency: number,
	server_hardware_polling_frequency: number,
	settingsSocket: WebSocket
}

export default class Settings extends Component<Props> {
	constructor(props: Props) {
			super(props)
	}

  woc_root = (key: string, value: number|string) => {
    const {settingsSocket} = this.props
    if ((!isNaN(value)) && (value != "")) {
      settingsSocket.send(JSON.stringify({key: key, value: value, label: "root"}))
    }
  }

  render() {
		const {datastreams_meta, server_transmit_frequency, server_hardware_polling_frequency} = this.props
    return (
      <div id="settingsDiv">
				<label htmlFor="smf" className="settingsClass">
					<div>Server measure delay (seconds between measurements):&nbsp;&nbsp;</div>
					<input id="smf" type="number" min="1"
						onChange={(e) => this.woc_root('polling_delay',e.target.value)}
						value={server_hardware_polling_frequency}
					/>
				</label>
				<label htmlFor="std" className="settingsClass">
					<div>Server transmit delay (seconds between sending latest measurement to web interface):&nbsp;&nbsp;</div>
					<input id="std" type="number" min="1"
						onChange={(e) => this.woc_root('transmit_delay',e.target.value)}
						value={server_transmit_frequency}
					/>
				</label>
      </div>
    )
  }
}
