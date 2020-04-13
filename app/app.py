import os
from flask import Flask, request, render_template, jsonify
from search import search
from data.parameters import R0, INC_PER, REC_TIME, TIME_STEPS
import pandas as pd
import func
import dash
import dash_core_components as dcc
import dash_html_components as html

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
		historical_plot = func.create_plot_from_data(historical_df)

		# Get data from the form with sliders
		R_0 = float(request.args.get('r_0', R0))
		inc_per = float(request.args.get('inc_per', INC_PER))
		rec_time = float(request.args.get('rec_time', REC_TIME))
		time_steps = int(request.args.get('time_steps', TIME_STEPS))
		
		params = (R_0, inc_per, rec_time, time_steps)
		simulation_plot = func.base_seir_model(params, time_steps, historical_df, last_updated)

	return render_template('simulation.html', 
		historical_plot=historical_plot, 
		last_updated=str(last_updated),
		R_0 = str(R_0),
		inc_per = str(inc_per),
		rec_time = str(rec_time),
		time_steps = str(time_steps),
		simulation_plot = simulation_plot)


if __name__ == '__main__':
	app.run(debug=True)