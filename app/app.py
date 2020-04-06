import os
from flask import Flask, request, render_template, jsonify
from search import search

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

if __name__ == '__main__':
	app.run(debug=True)