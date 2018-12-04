// @flow
import React, { Component } from 'react'

type Props = {
	seconds_between_updating_live_stream: number,
	seconds_between_storing_measurements: number,
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
		const {seconds_between_updating_live_stream, seconds_between_storing_measurements} = this.props
    return (
      <div id="settingsDiv">
				<label htmlFor="smf" className="settingsClass">
					<div>Seconds between updating live stream:&nbsp;&nbsp;</div>
					<input id="smf" type="number" min="1"
						onChange={(e) => this.woc_root('seconds_between_updating_live_stream',e.target.value)}
						value={seconds_between_updating_live_stream}
					/>
				</label>
				<label htmlFor="std" className="settingsClass">
					<div>Seconds between storing measurements on server:&nbsp;&nbsp;</div>
					<input id="std" type="number" min="1"
						onChange={(e) => this.woc_root('seconds_between_storing_measurements',e.target.value)}
						value={seconds_between_storing_measurements}
					/>
				</label>
      </div>
    )
  }
}
