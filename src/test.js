var ctx = document.getElementById("myChart");
var scatterChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: [{t: Date.now()+300,y: 0}, {t: Date.now()+600,y: 10}, {t: Date.now()+1000,y: 5}],
            fill: false,
            borderColor: 'red',
        }]
    },
    options: {
		animation: {
						easing: "linear",
            duration: 100, // general animation time
        },
        hover: {
            animationDuration: 0, // duration of animations when hovering an item
        },
        responsiveAnimationDuration: 0, // animation duration after a resize
      showLines: true,
    	elements: {line: { tension: 0}},
      scales: {xAxes: [{
				type: 'time',
				position: 'bottom', 
				ticks: {
					//minRotation: 90,
					//source: 'labels'
				}, 
				time: {min: Date.now()-10000, max: Date.now()}}]}
    }
});

function updateit() {
	if (scatterChart.data.datasets[0].data.length > 100) {
		scatterChart.data.datasets[0].data.shift()
	}
	
	scatterChart.data.datasets[0].data.push({t: Date.now(), y:50})
	scatterChart.options.scales.xAxes[0].time.min = Date.now()-10000
	scatterChart.options.scales.xAxes[0].time.max = Date.now()
	scatterChart.update()
}

setInterval(updateit, 100);