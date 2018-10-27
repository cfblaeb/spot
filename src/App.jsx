// @flow
import React, { Component} from 'react'
import CssBaseline from '@material-ui/core/CssBaseline'
import Graph from './graph.jsx'
import Paper from '@material-ui/core/Paper'

type Props = {
	datastreams_meta: {[string]: {[string]: string }},
	server_transmit_frequency: number,
	settingsSocket: WebSocket,
}

class App extends Component<Props>{
	chart_refs: {[string]: {current: null | Graph }}
	constructor(props: Props) {
			super(props)
			this.chart_refs = Object.assign(...Object.keys(props.datastreams_meta).map(key => ({[key]: React.createRef()})))
	}

	newServerData = (data: {[string]: number}) => {
		//'temperature': 10, 'pressure': 1000, 'humidity':50, 'ts':time(), 'date': str(datetime.now())
		Object.keys(this.props.datastreams_meta).forEach((key: string, index: number) => {
			if (this.chart_refs.hasOwnProperty(key) && this.chart_refs[key].current != null) {
				this.chart_refs[key].current.line_ref.current.chartInstance.config.data.datasets[0].data.push({
					x: data.ts*1000,  // python server sends time in seconds, but js expects ms
					y: data[key]
				})
				this.chart_refs[key].current.line_ref.current.chartInstance.update({preservation: true})
			}})
	}

	render(){
		return(
			<React.Fragment>
				<CssBaseline />
				<Paper className={"App"} elevation={10}>
				{Object.entries(this.props.datastreams_meta).map(([key: string, values: number], index) =>
					<Graph
						ref={this.chart_refs[key]}
						key={key}
						settingsSocket={this.props.settingsSocket}
						label={key}
						server_transmit_frequency={this.props.server_transmit_frequency}
						datastream_meta={this.props.datastreams_meta[key]}
					/>
				)}
				</Paper>
			</React.Fragment>
		)
	}
}

export default App
