// @flow
import {Line} from 'react-chartjs-2'
import React, { Component } from 'react'

type Props = {
  label: string,
  datastream_meta: {[string]: string },
  settingsSocket: WebSocket
}
type State = {
	graph_options: {}
}

export default class DTGraph extends Component<Props, State> {
	line_ref: {current: null | Line }
	constructor(props: Props) {
		super(props)
		this.line_ref = React.createRef()
		this.state = {
			graph_options: {
				legend: {display: false,}, maintainAspectRatio: true,
		    scales: {
		      xAxes: [{
						//type: 'time',
						time: {displayFormats: {millisecond: 'HH:mm:ss.SSS', second: 'HH:mm:ss', minute:'HH:mm', hour:	'HH'},}
					}],
					yAxes: [{
		        position: 'right',
		        scaleLabel: {display: true, fontSize: 16, fontStyle: 'bold',fontColor: this.props.datastream_meta['color'],labelString: this.props.datastream_meta['y_axis_label'],},
		      }],
				}
			}
		}
	}

  render() {
		const {label, datastream_meta} = this.props
		const {graph_options} = this.state
    return (
      <div>
        <Line
          ref={this.line_ref}
          data={{datasets: [{label: label,pointBackgroundColor: datastream_meta['color'],data: []}]}}
          width={parseInt(datastream_meta['plot_width'])}
          height={parseInt(datastream_meta['plot_height'])}
          options={graph_options}
        />
        <div>
          <label htmlFor={label+"_date_from"}>
            Start date:&nbsp;&nbsp;
            <input
              id={label+"_date_from"}
              type="date"
              //className="x_seconds_class"
              //onChange={(e) => this.woc('x_axis_seconds',e.target.value)}
              //value={datastream_meta['x_axis_seconds']}
            />
          </label>
          <label htmlFor={label+"_date_to"}>
            End date:&nbsp;&nbsp;
            <input
              id={label+"_date_to"}
              type="date"
              //className="x_seconds_class"
              //onChange={(e) => this.woc('x_axis_seconds',e.target.value)}
              //value={datastream_meta['x_axis_seconds']}
            />
          </label>
          <button>download visible data</button>
        </div>
      </div>
    )
    /*
			<div>
				<Line
					ref={this.line_ref}
					data={{datasets: [{label: label,pointBackgroundColor: datastream_meta['color'],data: []}]}}
					width={parseInt(datastream_meta['plot_width'])}
					height={parseInt(datastream_meta['plot_height'])}
					options={graph_options}
				/>
				<div>start date</div>
				<div>end date</div>
        <div>download visible data</div>
			</div>
		)*/
  }
}
