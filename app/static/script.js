$("#historical_btn").click(function(event){
  event.preventDefault();
  make_historical_request();
});

$("#forecast_btn").click(function(event){
  event.preventDefault();
  make_forecast_request();
});

function make_historical_request() {
	$.ajax({
		url: '/simulation',
		type: 'POST',
		data: {btn: 'historical_btn'},
		dataType: "json",
		success: function(data){

			var form_id = document.getElementById('form_id')
			if (form_id){
				document.getElementById('slider_form_container').removeChild(form_id);
			}

			var title = document.getElementById("plot_title");
			title.textContent = 'Plot of Historical Data (Last Updated : ' + data['last_updated'] + ')';
			var graphDiv = document.getElementById('historical_chart');
			plot = JSON.parse(data['plot']);
			Plotly.newPlot(graphDiv, plot, {});
		}
	});
}

function make_simulation_request(req_data) {
	$.ajax({
		url: '/simulation',
		type: 'POST',
		data: {btn: 'simulate_btn', 
			r_0: req_data['r_0'], 
			inc_per: req_data['inc_per'], 
			rec_time: req_data['rec_time'], 
			time_steps: req_data['time_steps']},
		dataType: "json",
		success: function(data){
			var title = document.getElementById("plot_title");
			title.textContent = 'Simulation of COVID-19 Virus Effects in Canada';
			populate_slider_form(data);
			var graphDiv = document.getElementById('historical_chart')
			plot = JSON.parse(data['plot'])
			Plotly.newPlot(graphDiv, plot, {});
			console.log(data);
		}
	});	
}

function make_forecast_request() {
	$.ajax({
		url: '/simulation',
		type: 'POST',
		data: {btn: 'forecast_btn'},
		dataType: "json",
		success: function(data){
			var title = document.getElementById("plot_title");
			title.textContent = 'Simulation of COVID-19 Virus Effects in Canada';
			populate_slider_form(data);
			var graphDiv = document.getElementById('historical_chart')
			plot = JSON.parse(data['plot'])
			Plotly.newPlot(graphDiv, plot, {});
		}
	});
}

function populate_single_slider(p_text, slider_value, name, input_id, output_id, max, min, step) {
	var slider = document.createElement('div');
	slider.setAttribute('class','slider');

	var text = document.createElement('p')
	text.textContent = p_text;

	var input = document.createElement('input');
	input.classList.add('mr-2');
	input.setAttribute('type', 'range');
	input.setAttribute('name', name);
	input.setAttribute('id', input_id);
	input.setAttribute('value', slider_value);
	input.setAttribute('min', min);
	input.setAttribute('max', max);
	input.setAttribute('step', step);
	input.setAttribute('oninput', output_id + '.value = ' + input_id + '.value');

	var output = document.createElement('output');
	output.setAttribute('name',input_id + '_out');
	output.setAttribute('id', output_id);
	output.textContent = slider_value;

	slider.appendChild(text);
	slider.appendChild(input);
	slider.appendChild(output);
	return slider
}

function populate_slider_form(data) {

	if (document.getElementById("form_id")){
		return
	}

	// Slider Values
	var R_0 = data['R_0'];
	var inc_per = data['inc_per'];
	var rec_time = data['rec_time'];
	var time_steps = data['time_steps'];

	var form_container = document.getElementById('slider_form_container');
	var form = document.createElement('form');
	form.setAttribute('id', 'form_id')
	form.setAttribute("action", '/simulation');

	var row_div = document.createElement('div');
	row_div.classList.add('row');

	// Reproduction Number Slider
	var col1_div = document.createElement('div');
	col1_div.classList.add('col-sm');

	var reproduction_slider = populate_single_slider("Reproduction Number",
		R_0, 
		'r_0', 
		'r_0_id', 
		'r_0_out_id', 
		'10', 
		'0', 
		'0.05');

	col1_div.appendChild(reproduction_slider);

	// Incubation Period Slider
	var col2_div = document.createElement('div');
	col2_div.classList.add('col-sm');

	var incubation_slider = populate_single_slider("Incubation Period", 
		inc_per, 
		'inc_per', 
		'inc_per_id', 
		'inc_per_out_id',
		'31',
		'0',
		'1');

	col2_div.appendChild(incubation_slider);

	//Recovery Time Slider
	var col3_div = document.createElement('div');
	col3_div.classList.add('col-sm');

	var recovery_slider = populate_single_slider("Recovery Time", 
		rec_time, 
		'rec_time', 
		'rec_time_id', 
		'rec_time_out_id',
		'31',
		'0',
		'1');

	col3_div.appendChild(recovery_slider);
	
	//Time Steps Slider
	var col4_div = document.createElement('div');
	col4_div.classList.add('col-sm');

	var time_slider = populate_single_slider("Time Steps", 
		time_steps, 
		'time_steps', 
		'time_steps_id', 
		'time_steps_out_id',
		'730',
		'1',
		'1');

	col4_div.appendChild(time_slider);

	row_div.appendChild(col1_div);
	row_div.appendChild(col2_div);
	row_div.appendChild(col3_div);
	row_div.appendChild(col4_div);

	// Simulate Button
	var button_container = document.createElement('div');
	button_container.classList.add('mt-3');
	button_container.classList.add('d-flex');
	button_container.classList.add('justify-content-center');

	var simulate_btn = document.createElement('button');
	simulate_btn.setAttribute('id', 'simulate_btn');
	simulate_btn.setAttribute('type', 'submit');
	simulate_btn.classList.add('btn');
	simulate_btn.classList.add('btn-primary');
	simulate_btn.textContent = 'Simulate';

	button_container.appendChild(simulate_btn);

	form.appendChild(row_div);
	form.appendChild(button_container);
	form_container.appendChild(form);

	$("#simulate_btn").click(function(event){
		event.preventDefault();
		var r_0 = document.getElementById('r_0_out_id').textContent;
		var inc_per = document.getElementById('inc_per_out_id').textContent;
		var rec_time = document.getElementById('rec_time_out_id').textContent;
		var time_steps = document.getElementById('time_steps_out_id').textContent;
		var req_data = {
			r_0: r_0,
			inc_per: inc_per,
			rec_time: rec_time,
			time_steps: time_steps,
		}
		make_simulation_request(req_data);
	});

}