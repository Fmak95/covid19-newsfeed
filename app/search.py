from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from bs4 import BeautifulSoup
import pdb
from datetime import datetime

class NewsArticle():
	def __init__(self, title, description, link, pubDate):
		self.title = title
		self.description = description
		self.link = link
		date = datetime.strptime(pubDate, '%Y/%m/%d %H:%M:%S')
		self.pubDate = date #datetime obj for sorting
		self.displayDate = datetime.strftime(date, '%a, %d %b %Y %H:%M:%S') #string for human readability

	def from_doc(self, doc):
		return NewsArticle(doc.title, doc.description, doc.link, doc.pubDate)

def search(search_term, num_results):
	'''
		Searches ES database and returns list of NewsArticle objects
	'''
	es = Elasticsearch('http://localhost:9200')
	news_articles = []

	# Searching Title of News Article
	query = {
		"match": {
			"title": {
				"query": search_term
			}
		}
	}
	s = Search(using=es)
	docs = s.query(query)[:num_results].execute()

	for doc in docs:
		title = doc.title
		description = clean_text(doc.description)
		link = doc.link
		pubDate = doc.pubDate
		news_articles.append(NewsArticle(title, description, link, pubDate))

	return news_articles

def clean_text(text):
	'''
		This function takes in a string argument and makes it human readable:
		- Removes html tags
	'''
	soup = BeautifulSoup(text, features='lxml')
	return soup.get_text()