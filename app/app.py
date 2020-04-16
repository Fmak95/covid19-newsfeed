import os
from flask import Flask, request, render_template, jsonify, make_response
from search import search
from data.parameters import R0, INC_PER, REC_TIME, TIME_STEPS, START_DATE
import pandas as pd
import func
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly

historical_df, last_updated = func.get_covid_data()
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
	news_articles = search('COVID-19', 10) #Default search term
	return render_template('index.html', news_articles = news_articles)

@app.route('/search', methods = ['GET', 'POST'])
def search_news():
	if request.method == 'GET':
		sort_by = request.args.get('sort_by')
		query = request.args.get('search')
		news_articles = search(query, 10)

		if sort_by == 'date':
			news_articles = sorted(news_articles, key=lambda x: x.pubDate, reverse=True)

	return render_template('index.html', news_articles = news_articles)

@app.route('/simulation', methods = ['GET', 'POST'])
def simulation():

	if request.method == 'GET':
		plot = func.create_plot_from_data(historical_df)
		return render_template('simulation.html', 
			last_updated=str(last_updated),
			plot=plot)

	if request.method == 'POST':
		btn = request.form['btn']

		if btn == 'historical_btn':
			plot = func.create_plot_from_data(historical_df)
			payload = {'last_updated': last_updated, 'plot': plot}

		if btn == 'forecast_btn' or btn == 'simulate_btn':
			# Get data from the form with sliders
			R_0, inc_per, rec_time, time_steps, _ = get_data_from_sliders()
			params = (R_0, inc_per, rec_time, time_steps)
			plot = func.base_seir_model(params, time_steps, historical_df, last_updated)
			payload = {'last_updated': last_updated, 
				'plot': plot,
				'R_0': R_0,
				'inc_per': inc_per,
				'rec_time': rec_time,
				'time_steps': time_steps}

		resp = make_response(payload)
		resp.status_code = 200
		resp.headers['Access-Control-Allow-Origin'] = '*'
		return resp

@app.route('/tuning', methods= ['GET', 'POST'])
def tuning():
	R_0, inc_per, rec_time, time_steps, start_date = get_data_from_sliders()
	params = (R_0, inc_per, rec_time, time_steps)

	if request.method == "GET":
		plot = func.create_tuning_plot(params, historical_df)
		payload = {
			'plot': plot,
			'R_0': R_0,
			'inc_per': inc_per,
			'rec_time': rec_time,
			'time_steps': time_steps
		}

	if request.method == "POST":
		R_0, inc_per, rec_time, _, start_date = get_data_from_sliders()
		print(start_date, _)
		params = (R_0, inc_per, rec_time, time_steps)
		plot = func.create_tuning_plot(params, historical_df, start_date=start_date)
		payload = {
			'plot': plot,
			'R_0': R_0,
			'inc_per': inc_per,
			'rec_time': rec_time,
			'time_steps': time_steps
		}

	resp = make_response(payload)
	resp.status_code = 200
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

def get_data_from_sliders():
	R_0 = float(request.form.get('r_0', R0))
	inc_per = float(request.form.get('inc_per', INC_PER))
	rec_time = float(request.form.get('rec_time', REC_TIME))

	try:
		time_steps = int(request.form.get('time_steps',TIME_STEPS))
	except:
		time_steps = None

	try:
		start_date = request.form.get('start_date', START_DATE)
	except:
		start_date = None

	return R_0, inc_per, rec_time, time_steps, start_date

if __name__ == '__main__':
	app.run(debug=True)