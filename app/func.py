import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.parameters import CDR
import plotly.express as px
import plotly
import plotly.graph_objs as go
import json
import os

def get_covid_data():
	'''
	Gets covid data from the Johhn Hopkins Repo
	https://github.com/CSSEGISandData/COVID-19
	'''
	JHU_GLOBAL_CONFIRMED = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
	JHU_GLOBAL_RECOVERED = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
	JHU_GLOBAL_DEATHS = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

	# Get data from John Hopkins Repo
	global_confirmed = pd.read_csv(JHU_GLOBAL_CONFIRMED).rename(columns = {'Country/Region':'Country'})
	global_recovered = pd.read_csv(JHU_GLOBAL_RECOVERED).rename(columns = {'Country/Region':'Country'})
	global_deaths = pd.read_csv(JHU_GLOBAL_DEATHS).rename(columns = {'Country/Region':'Country'})

	# Filter data for Canada Only
	global_confirmed = global_confirmed[global_confirmed.Country == 'Canada']
	global_recovered = global_recovered[global_recovered.Country == 'Canada']
	global_deaths = global_deaths[global_deaths.Country == 'Canada']

	last_updated = global_confirmed.columns[-1]
	historical_df = _create_historical_df(global_confirmed, global_recovered, global_deaths)
	return historical_df, last_updated

def _create_historical_df(global_confirmed, global_recovered, global_deaths):
	'''
	Converts raw data obtained from the Johhn Hopkins Repo
	and returns a single dataframe with the relevant information

	date
	num_confirmed
	num_recovered
	num_deaths
	'''
	historical_df = pd.DataFrame()
	dates =  [datetime.strptime(date, '%m/%d/%y') \
	          for date in global_confirmed.drop(['Province/State','Country','Lat','Long'],axis=1).sum(axis=0).index]

	num_confirmed = global_confirmed.drop(['Province/State', 'Country', 'Lat', 'Long'],axis=1)
	num_confirmed = num_confirmed.sum(axis=0).values

	num_recovered = global_recovered.drop(['Province/State', 'Country', 'Lat', 'Long'],axis=1)
	num_recovered = num_recovered.sum(axis=0).values

	num_deaths = global_deaths.drop(['Province/State', 'Country', 'Lat', 'Long'],axis=1)
	num_deaths = num_deaths.sum(axis=0).values

	historical_df['date'] = dates
	historical_df['num_confirmed'] = num_confirmed
	historical_df['num_recovered'] = num_recovered
	historical_df['num_deaths'] = num_deaths

	return historical_df

def create_plot_from_data(data):
	fig = px.line(data.melt(id_vars='date'), x="date", y="value", color='variable')
	return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def init_social_demographic_data():
	'''
	Combines Canadian demographic data taken from: 
		https://www.populationpyramid.net/canada/2019/
	and data taken from a study down on COVID-19, grouped by age groups:
		https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf

	Returns a pandas dataframe with the following info:
		- Age group
		- Total Population
		- Distribution
		- Hospitalization Rate
		- Hospitalized Death Rate
	'''
	dirname = os.path.dirname(__file__)
	filename = os.path.join(dirname, 'data/age_data_canada_2019.csv')
	age_data_df = pd.read_csv(filename)
	age_data_df['distribution'] = age_data_df.population / age_data_df.population.sum()

	# Add Data related to study: 
	#https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf
	age_data_df.loc[age_data_df.Age=='0-9','hospitalization_rate'] = 0.001
	age_data_df.loc[age_data_df.Age=='10-19','hospitalization_rate'] = 0.003
	age_data_df.loc[age_data_df.Age=='20-29','hospitalization_rate'] = 0.012
	age_data_df.loc[age_data_df.Age=='30-39','hospitalization_rate'] = 0.032
	age_data_df.loc[age_data_df.Age=='40-49','hospitalization_rate'] = 0.049
	age_data_df.loc[age_data_df.Age=='50-59','hospitalization_rate'] = 0.102
	age_data_df.loc[age_data_df.Age=='60-69','hospitalization_rate'] = 0.166
	age_data_df.loc[age_data_df.Age=='70-79','hospitalization_rate'] = 0.243
	age_data_df.loc[age_data_df.Age=='80+','hospitalization_rate'] = 0.273

	age_data_df.loc[age_data_df.Age=='0-9','hospitalized_death_rate'] = 0.00002
	age_data_df.loc[age_data_df.Age=='10-19','hospitalized_death_rate'] = 0.00006
	age_data_df.loc[age_data_df.Age=='20-29','hospitalized_death_rate'] = 0.0003
	age_data_df.loc[age_data_df.Age=='30-39','hospitalized_death_rate'] = 0.0008
	age_data_df.loc[age_data_df.Age=='40-49','hospitalized_death_rate'] = 0.0015
	age_data_df.loc[age_data_df.Age=='50-59','hospitalized_death_rate'] = 0.006
	age_data_df.loc[age_data_df.Age=='60-69','hospitalized_death_rate'] = 0.022
	age_data_df.loc[age_data_df.Age=='70-79','hospitalized_death_rate'] = 0.051
	age_data_df.loc[age_data_df.Age=='80+','hospitalized_death_rate'] = 0.093
	return age_data_df

def _get_init_values_for_model(historical_df, start_date):
	'''
	Return the Initial Values needed for SIER Model:
	- Initial number of people Susceptible
	- Initial number of people Exposed
	- Initial number of people Infected
	- Initial number of people Removed
	- Disease Transmission Rate
	- Disease Incubation Period
	- Disease Recovery Rate
	'''

	N = 37411038 # Population of Canada

	# Exposed = (num_confirmed - num_recovered - num_deaths) * (1 - reporting_rate / reporting_rate)
	RR = 0.75
	E_0 = (historical_df[historical_df.date == start_date].num_confirmed.values[0]\
	        - historical_df[historical_df.date == start_date].num_recovered.values[0]\
	        - historical_df[historical_df.date == start_date].num_deaths.values[0])\
	    * ((1 - RR) / RR)
	E_0 = round(E_0)

	# Infected = num_confirmed - (num_recovered + num_deaths)
	I_0 = historical_df[historical_df.date == start_date].num_confirmed.values[0]\
		- historical_df[historical_df.date == start_date].num_recovered.values[0]\
	    - historical_df[historical_df.date == start_date].num_deaths.values[0]

	# Recovered
	R_0 = historical_df[historical_df.date == start_date].num_recovered.values[0]

	# Deaths
	D_0 = historical_df[historical_df.date == start_date].num_deaths.values[0]

	# Susceptible = Total Population - (Exposed + Infected + Removed)
	S_0 = N - (E_0 + I_0 + R_0 + D_0)

	return S_0, E_0, I_0, R_0, D_0

def _get_model_hyperparams(params):
	'''
	Takes in the raw statistics of the disease and returns:
		beta - Infectious rate of disease (probability of transmitting disease from infected to susceptible person)
		sigma - Incubation rate (rate of latent individuals becoming infectious)
		gamma - Recovery rate

	For more detail of beta, sigma and gamma see:
		https://www.idmod.org/docs/hiv/model-seir.html#seirs-model
	'''
	R_0, inc_per, rec_time, time_steps = params
	sigma = 1/inc_per
	gamma = 1/rec_time
	beta = R_0*gamma
	return beta, sigma, gamma

def base_seir_model(params, time_steps, historical_df, start_date, 
					value_vars = ['Exposed','Infected','Hospitalized', 'Total Deaths']):
	'''
	SEIR Model to forecast the outcome of the COVID-19 pandemic.
	For more details about the model see this link:
		https://www.idmod.org/docs/hiv/model-seir.html#seirs-model
	'''

	################### TO DO #######################
	# Add num hospitalized and num of deaths
	if type(start_date) == str:
		start_date = datetime.strptime(start_date, '%m/%d/%y')

	S_0, E_0, I_0, R_0, D_0 = _get_init_values_for_model(historical_df, start_date)
	age_data_df = init_social_demographic_data()
	num_hospital_beds = 93527

	# Estimate initial people in hospital using social demographic data
	round(I_0 * age_data_df.distribution * age_data_df.hospitalization_rate).sum()
	H_0 = round(I_0 * age_data_df.distribution * age_data_df.hospitalization_rate).sum()

	N = S_0 + E_0 + I_0 + R_0 + D_0 # Total Population
	beta, sigma, gamma = _get_model_hyperparams(params)
	
	S, E, I, R, D, H = [S_0], [E_0], [I_0], [R_0], [D_0], [H_0]
	dates = [start_date]

	# Start simulation
	for i in range(1,time_steps+1):
		date = dates[-1] + timedelta(days=1)
		next_S = S[-1] - (beta*S[-1]*I[-1])/N
		next_E = E[-1] + (beta*S[-1]*I[-1])/N - sigma*E[-1]
		next_I = I[-1] + (sigma*E[-1] - gamma*I[-1])
		next_R = R[-1] + (gamma*I[-1])

		# current hospital count = current infected * age distribution * hospitalization rate
		next_H = round(next_I * age_data_df.distribution * age_data_df.hospitalization_rate).sum()

		# If hospital care avaialble, death rate is lower
		if next_H <= num_hospital_beds:
			next_D = D[-1] + round(next_H * age_data_df.distribution * age_data_df.hospitalized_death_rate).sum()
		# If hospital care unabailable, death rate is higher (we use the critical death rate, CDR, which is ~12%)
		# CDR gotten from: https://wwwnc.cdc.gov/eid/article/26/6/20-0233_article
		else:
			deaths_with_hospital_care = round(num_hospital_beds * age_data_df.distribution * age_data_df.hospitalized_death_rate).sum()
			deahts_no_hospital_care = round((next_H - num_hospital_beds) * CDR)
			next_D = D[-1] + deaths_with_hospital_care + deahts_no_hospital_care

		S.append(next_S)
		E.append(next_E)
		I.append(next_I)
		R.append(next_R)
		H.append(next_H)
		D.append(next_D)
		dates.append(date)

	results_df = pd.DataFrame({
		'dates': dates,
		'Susceptible': S,
		'Exposed': E,
		'Infected': I,
		'Recovered': R,
		'Hospitalized': H,
		'Total Deaths': D})
	
	results_df = results_df.melt(id_vars='dates',value_vars = value_vars)
	plot = px.line(results_df, x='dates', y='value', color='variable')

	return json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)






