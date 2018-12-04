// @flow
import {Line} from "react-chartjs-2"
import React, {Component} from "react"

type Props = {
	label: string,
	datastream_meta: {
		color: string,
		y_axis_label: string,
		plot_width: number,
		plot_height: number
	},
}
type State = {
	graph_options: {},
	start_time: string,
	end_time: string,
	visible_data: Array<Object>
}

export default class DTGraph extends Component<Props, State> {
	line_ref: { current: null | Line }

	constructor(props: Props) {
		super(props)
		this.line_ref = React.createRef()
		this.state = {
			visible_data: [],
			start_time: (new Date(Date.now() - 1000 * 60 * 60 * 24 * 30)).toISOString().substring(0, 10),
			end_time: (new Date).toISOString().substring(0, 10),
			graph_options: {
				plugins: {streaming: false},
				legend: {display: false,}, maintainAspectRatio: true,
				scales: {
					xAxes: [{
						type: "time",
						time: {
							displayFormats: {
								millisecond: "HH:mm:ss.SSS", second: "HH:mm:ss", minute: "HH:mm", hour: "HH"
							},
						}
					}],
					yAxes: [{
						position: "right",
						scaleLabel: {
							display: true, fontSize: 16, fontStyle: "bold",
							fontColor: this.props.datastream_meta["color"],
							labelString: this.props.datastream_meta["y_axis_label"],
						},
					}],
				}
			}
		}
	}

	set_start_time = (time: string) => {
		this.setState({"start_time": time})
		this.fetch_data(time, this.state.end_time)
	}
	set_end_time = (time: string) => {
		this.setState({"end_time": time})
		this.fetch_data(this.state.start_time, time)
	}

	fetch_data = (start_time: string, end_time: string) => {
		if (start_time && end_time) {
			const {label} = this.props
			fetch("/historic_json/" + label + "/" + start_time + "/" + end_time)
				.then(r => r.json())
				.then(data => this.setState({visible_data: JSON.parse(data)}))
				.catch(e => console.log(e))
		}
	}

	componentDidMount(): void {
		this.fetch_data(this.state.start_time, this.state.end_time)
	}

	render() {
		const {label, datastream_meta} = this.props
		const {graph_options, visible_data, start_time, end_time} = this.state
		const donwload_link = label + "_" + start_time + "_" + end_time + ".xlsx"
		return (
			<div>
				<Line
					ref={this.line_ref}
					data={{datasets: [{label: label, pointBackgroundColor: datastream_meta["color"], data: visible_data}]}}
					width={parseInt(datastream_meta["plot_width"])}
					height={parseInt(datastream_meta["plot_height"])}
					options={graph_options}
				/>
				<div>
					<label htmlFor={label + "_date_from"}>
						Start date:&nbsp;&nbsp;
						<input
							id={label + "_date_from"}
							type="date"
							//className="x_seconds_class"
							onChange={(e) => this.set_start_time(e.target.value)}
							value={start_time}
						/>
					</label>
					<label htmlFor={label + "_date_to"}>
						End date:&nbsp;&nbsp;
						<input
							id={label + "_date_to"}
							type="date"
							//className="x_seconds_class"
							onChange={(e) => this.set_end_time(e.target.value)}
							value={end_time}
						/>
					</label>
					<a href={donwload_link}>
						<button type='button'>Download visible data</button>
					</a>
				</div>
			</div>
		)
	}
}
