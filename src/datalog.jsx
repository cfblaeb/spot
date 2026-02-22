import {Line} from "react-chartjs-2"
import React, {Component} from "react"

export default class DTGraph extends Component {
  constructor(props) {
    super(props)
    this.line_ref = React.createRef()
    this.state = {
      visible_data: [],
      start_time: (new Date(Date.now() - 1000 * 60 * 60 * 24 * 30)).toISOString().substring(0, 10),
      end_time: (new Date(Date.now() + 1000 * 60 * 60 * 24)).toISOString().substring(0, 10),
      graph_options: {
        plugins: {
          streaming: false,
          legend: {display: false,},
        },
        maintainAspectRatio: true,
        scales: {
          x: {
            type: "time",
            time: {
              displayFormats: {
                day: 'MMM d',
                hour: 'HH:mm',
                minute: 'HH:mm',
                second: 'HH:mm:ss',
              }
            }
          },
          y: {
            position: "right",
            title: {
              display: true,
              text: this.props.datastream_meta["y_axis_label"],
              color: this.props.datastream_meta["color"],
              font: {
                size: 16,
                weight: "bold",
              }
            },
          },
        }
      }
    }
  }

	set_start_time = (time) => {
		this.setState({"start_time": time})
		this.fetch_data(time, this.state.end_time)
	}
	set_end_time = (time) => {
		this.setState({"end_time": time})
		this.fetch_data(this.state.start_time, time)
	}

	fetch_data = (start_time, end_time) => {
		if (start_time && end_time) {
			const {label} = this.props
			fetch("/historic_json/" + label + "/" + start_time + "/" + end_time)
				.then(r => r.json())
				.then(data => this.setState({visible_data: JSON.parse(data)}))
				.catch(e => console.log(e))
		}
	}

	componentDidMount() {
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