// @flow
import {Line} from 'react-chartjs-2'
import React, { Component } from 'react'

type Props = {
  label: string,
  datastream_meta: {[string]: string },
  server_transmit_frequency: number,
  settingsSocket: WebSocket,
}

type State = {settings_open: boolean}

export default class RTGraph extends Component<Props, State> {
  line_ref: {current: null | Line }
  graph_options: {}

  constructor(props: Props) {
    super(props)
    this.line_ref = React.createRef()
    this.graph_options = this.convertMetaToOptions(this.props.datastream_meta, this.props.label, this.props.server_transmit_frequency)
    this.state = {settings_open: false}
  }

  convertMetaToOptions = (meta: {[string]: string }, label: string, server_transmit_frequency: number) => {
    /*"temperature": {"color": "#FF0000", "plot_width": 1000, "plot_height": 200, "x_axis_seconds": 10, "y_axis_label": "celcius"},}*/
    return {
      legend: {display: false,}, maintainAspectRatio: true,
      scales: {
        xAxes: [{
          type: 'realtime',
          realtime:{
            duration: parseInt(meta['x_axis_seconds'])*1000,
            delay: server_transmit_frequency*1000*2,
            pause: false,
            //frameRate: 50,
          }, time: {displayFormats: {millisecond: 'HH:mm:ss.SSS', second: 'HH:mm:ss', minute:'HH:mm', hour:	'HH'},}}],
        yAxes: [{
          position: 'right',
          scaleLabel: {display: true, fontSize: 16, fontStyle: 'bold',fontColor: meta['color'],labelString: meta['y_axis_label'],},
        }],
      }
    }
  }

  componentDidUpdate(): void {
    const x_axis_seconds = parseInt(this.props.datastream_meta.x_axis_seconds)
    this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.duration = x_axis_seconds*1000
    //this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.delay = this.props.server_transmit_frequency*1000*2
    this.line_ref.current.chartInstance.update({preservation: true})
  }

  woc = (key: string, value: number|string) => {
    const {label} = this.props
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
          options={this.graph_options}
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
