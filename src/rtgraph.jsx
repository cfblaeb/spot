// @flow
import { Line } from 'react-chartjs-2'
import React, { Component } from 'react'

type Props = {
  label: string,
  datastream_meta: {
    x_axis_seconds: number,
    color: string,
    y_axis_label: string,
    plot_width: number,
    plot_height: number
  },
  seconds_between_updating_live_stream: number,
  settingsSocket: WebSocket,
}

type State = {
  settings_open: boolean,
  graph_options: {}
}

export default class RTGraph extends Component<Props, State> {
  line_ref: {current: null | Line }

  constructor(props: Props) {
    super(props)
    this.line_ref = React.createRef()
    this.state = {
      settings_open: false,
      graph_options: {
        legend: {display: false,}, maintainAspectRatio: true,
        scales: {
          xAxes: [{
            type: 'realtime',
            realtime:{
              duration: parseInt(this.props.datastream_meta.x_axis_seconds)*1000,
              delay: this.props.seconds_between_updating_live_stream*1000,
              pause: false,
              //frameRate: 50,
            }, time: {displayFormats: {millisecond: 'HH:mm:ss.SSS', second: 'HH:mm:ss', minute:'HH:mm', hour:	'HH'},}}],
          yAxes: [{
            position: 'right',
            scaleLabel: {
              display: true,
              fontSize: 16,
              fontStyle: 'bold',
              fontColor: this.props.datastream_meta.color,
              labelString: this.props.datastream_meta.y_axis_label,
            },
          }],
        }
      }
    }
  }

  componentDidUpdate(): void {
    const x_axis_seconds = parseInt(this.props.datastream_meta.x_axis_seconds)
    if (this.line_ref.current != null) {
      this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.duration = x_axis_seconds*1000
      //this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.delay = this.props.seconds_between_updating_live_stream*1000*2
      this.line_ref.current.chartInstance.update({preservation: true})
    }
  }

  woc = (key: string, value: number|string) => {
    const { label } = this.props
    if ((!isNaN(value)) && (value != "")) {
      this.props.settingsSocket.send(JSON.stringify({key: key, value: value, label: label}))
    }
  }

  render() {
    const {datastream_meta, label} = this.props
    return (
      <div className="graphClass">
        <div className="graphHeader" style={{color: datastream_meta.color}}>{label}</div>
        <Line
          ref={this.line_ref}
          data={{datasets: [{label: label,pointBackgroundColor: datastream_meta['color'],data: []}]}}
          width={parseInt(datastream_meta['plot_width'])}
          height={parseInt(datastream_meta['plot_height'])}
          options={this.state.graph_options}
        />
        <label htmlFor={label+"_x_axis_seconds_input"}>
          Seconds to show:&nbsp;&nbsp;
          <input
            id={label+"_x_axis_seconds_input"}
            type="number"
            className="x_seconds_class"
            onChange={(e) => this.woc('x_axis_seconds',e.target.value)}
            value={datastream_meta['x_axis_seconds']}
            min="1"
          />
        </label>
      </div>
    )
  }
}