// @flow
import {Line} from 'react-chartjs-2'
import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper'
import ExpansionPanel from '@material-ui/core/ExpansionPanel'
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary'
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'
import Button from '@material-ui/core/Button'
import Switch from '@material-ui/core/Switch'
import Input from '@material-ui/core/Input'
import FormLabel from '@material-ui/core/FormLabel'
import FormControl from '@material-ui/core/FormControl'
import FormGroup from '@material-ui/core/FormGroup'
import FormControlLabel from '@material-ui/core/FormControlLabel'
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';

type Props = {
  label: string,
  datastream_meta: {[string]: string },
  server_transmit_frequency: number,
  settingsSocket: WebSocket
}

export default class Graph extends Component<Props> {
  line_ref: {current: null | Line }
  graph_options: {}
	constructor(props: Props) {
			super(props)
			this.line_ref = React.createRef()
      this.graph_options = this.convertMetaToOptions(this.props.datastream_meta, this.props.label, this.props.server_transmit_frequency)
	}
  convertMetaToOptions = (meta: {[string]: string }, label: string, server_transmit_frequency: number) => {
    /*"temperature": {"color": "#FF0000", "plot_width": 1000, "plot_height": 200,
      "x_axis_seconds": 10, "y_axis_label": "celcius", "y_axis_from": -50, "y_axis_to": 50,
      "visible": true},
      }*/
    return {
      title: {display: true, text: label, fontSize: 16, fontStyle: 'bold', fontColor: meta['color'],},
      legend: {display: false,},
      maintainAspectRatio: true,
      scales: {
        xAxes: [{
          type: 'realtime',
          realtime:{
            duration: parseInt(meta['x_axis_seconds'])*1000,
            delay: server_transmit_frequency*1000*2,
            //frameRate: 50,
            pause: false
          },
          time: {displayFormats: {millisecond: 'HH:mm:ss.SSS', second: 'HH:mm:ss', minute:'HH:mm', hour:	'HH'},},
        }],
        yAxes: [{
          position: 'right',
          scaleLabel: {display: true, fontSize: 16, fontStyle: 'bold',fontColor: meta['color'],labelString: meta['y_axis_label'],},
          ticks: {min: parseInt(meta['y_axis_from']), max: parseInt(meta['y_axis_to'])}
        }],
      }
    }
  }
  componentDidUpdate = () => {
    const y_axis_from = parseInt(this.props.datastream_meta.y_axis_from)
    const y_axis_to = parseInt(this.props.datastream_meta.y_axis_to)
    const x_axis_seconds = parseInt(this.props.datastream_meta.x_axis_seconds)
    //this.line_ref.current.chartInstance.config.options.title.text = this.props.label
    //this.line_ref.current.chartInstance.config.options.title.fontColor = new_options['color']
    this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.duration = x_axis_seconds*1000
    //this.line_ref.current.chartInstance.config.options.scales.xAxes[0].realtime.delay = this.props.server_transmit_frequency*1000*2
    //this.line_ref.current.chartInstance.config.options.scales.yAxes[0].scaleLabel.fontColor = new_options['color']
    //this.line_ref.current.chartInstance.config.options.scales.yAxes[0].scaleLabel.labelString = new_options['y_axis_label']
    this.line_ref.current.chartInstance.config.options.scales.yAxes[0].ticks.min = y_axis_from
    this.line_ref.current.chartInstance.config.options.scales.yAxes[0].ticks.max = y_axis_to
    this.line_ref.current.chartInstance.update({preservation: true})
  }

  woc = (key: string, value: number|string) => {
    const {label} = this.props
    console.log(typeof(value))
    console.log(value)
    if ((!isNaN(value)) && (value != "")) {
      this.props.settingsSocket.send(JSON.stringify({key: key, value: value, label: label}))
    }
  }
  render() {
    return (
      <Paper className={"agraph"} elevation={10}>
        <Line
          ref={this.line_ref}
          data={{datasets: [{label: this.props.label,pointBackgroundColor: this.props.datastream_meta['color'],data: []}]}}
          width={parseInt(this.props.datastream_meta['plot_width'])} height={parseInt(this.props.datastream_meta['plot_height'])}
          options={this.graph_options}
        />
        <ExpansionPanel>
          <ExpansionPanelSummary><Button variant="contained">Settings<ExpandMoreIcon /></Button></ExpansionPanelSummary>
          <ExpansionPanelDetails>
            <Card>
              <CardContent>
                <FormControl component="fieldset">
                  <FormLabel component="legend">Settings</FormLabel>
                  <FormGroup>
                    <FormControlLabel control={<Input type="number" onChange={(e) => this.woc('x_axis_seconds',e.target.value)} value={this.props.datastream_meta['x_axis_seconds']} inputProps={{min: 1}} />} label="visible time" />
                    <FormControlLabel control={<Input type="number" />} onChange={(e) => this.woc('y_axis_from',e.target.value)} value={this.props.datastream_meta['y_axis_from'].toString()} label="y axis mininum" />
                    <FormControlLabel control={<Input type="number" />} onChange={(e) => this.woc('y_axis_to',e.target.value)} value={this.props.datastream_meta['y_axis_to'].toString()} label="y axis maximum" />
                    <FormControlLabel control={<Switch/>} label="pause" />
                  </FormGroup>
                </FormControl>
              </CardContent>
            </Card>
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </Paper>
    )
  }
}
