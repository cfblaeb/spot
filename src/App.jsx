// @flow
import * as React from 'react'
import RTGraph from './rtgraph.jsx'
import DTGraph from './datalog.jsx'
import Settings from './settings.jsx'

type Props = {
	datastreams_meta: {[string]: {[string]: string }},
	server_transmit_frequency: number,
	server_hardware_polling_frequency: number,
	settingsSocket: WebSocket,
}
type State = {page: number}

export default class App extends React.Component<Props, State>{
	chart_refs: {[string]: {current: null | React.Element<typeof RTGraph> }}
	constructor(props: Props) {
		super(props)
		this.chart_refs = Object.assign(...Object.keys(props.datastreams_meta).map(key => ({[key]: React.createRef()})))
		this.state = {page: 0}
	}

	newServerData = (data: {[string]: number}) => {
		//'temperature': 10, 'pressure': 1000, 'humidity':50, 'ts':time(), 'date': str(datetime.now())
		const {page} = this.state
		const {datastreams_meta} = this.props
		if (page == 0) {
			Object.keys(datastreams_meta).forEach((key: string, index: number) => {
				if (this.chart_refs.hasOwnProperty(key) && this.chart_refs[key].current != null) {
					this.chart_refs[key].current.line_ref.current.chartInstance.config.data.datasets[0].data.push({
						x: data.ts * 1000,  // python server sends time in seconds, but js expects ms
						y: data[key]
					})
					this.chart_refs[key].current.line_ref.current.chartInstance.update({preservation: true})
				}
			})
		}
	}

	render() {
		const {page} = this.state
		const {server_transmit_frequency, server_hardware_polling_frequency, datastreams_meta, settingsSocket} = this.props
		let middlething = <div>missing</div>
		switch (page) {
			case 0:
				middlething = Object.entries(datastreams_meta).map(([key, values], index) =>
					<RTGraph
						ref={this.chart_refs[key]}
						key={key}
						settingsSocket={settingsSocket}
						label={key}
						server_transmit_frequency={server_transmit_frequency}
						datastream_meta={datastreams_meta[key]}
					/>
				)
				break;
			case 1:
				middlething = (
					<div>
						<a href="all_data"><button type="button">download all data</button></a>
						{Object.entries(datastreams_meta).map(([key, values], index) =>
							<DTGraph
								ref={this.chart_refs[key]}
								key={key}
								settingsSocket={settingsSocket}
								label={key}
								datastream_meta={datastreams_meta[key]}
							/>
						)}
					</div>
				)
				break;
			case 2:
				middlething =
					<Settings
						datastreams_meta={datastreams_meta}
						server_transmit_frequency={server_transmit_frequency}
						server_hardware_polling_frequency={server_hardware_polling_frequency}
						settingsSocket={settingsSocket}
					/>
				break;
		}
		return (
			<div id="frameDiv">
				<div id="topDiv">
					<div id="titleDiv">Data logger thingy</div>
					<div onClick={() => this.setState({page: 0})} className={page==0 ? 'menuButtons active' : 'menuButtons'}>Real time data</div>
					<div onClick={() => this.setState({page: 1})} className={page==1 ? 'menuButtons active' : 'menuButtons'}>Historic data</div>
					<div onClick={() => this.setState({page: 2})} className={page==2 ? 'menuButtons active' : 'menuButtons'}>Settings</div>
				</div>
				<div id="middleDiv">{middlething}</div>
				<div id="bottomDiv"><h2>by Dr. Lasse Ebdrup Pedersen&nbsp;&nbsp;</h2></div>
			</div>
		)
	}
}
