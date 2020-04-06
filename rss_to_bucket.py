'''
	Access RSS feeds from multiple news websites
	and store the data into an Amazon S3 bucket.

	CBC - 'Mon, 20 Jan 2020 17:11:33 EST'
	TheStar - 'Fri, 3 Apr 2020 11:31:00 EDT'
	CTV - 'Fri, 3 Apr 2020 10:13:00 -0400'
'''

import requests
from bs4 import BeautifulSoup
import pdb
from collections import defaultdict
from time import gmtime, strftime
import json
from settings import BUCKET_NAME
import boto3
from datetime import datetime

def rss_to_bucket():
	date = strftime("%Y-%m-%d", gmtime())
	s3 = boto3.resource('s3')
	news_headlines = []
	urls = [('http://www.thestar.com/feeds.topstories.rss', 'thestar'), 
		('https://rss.cbc.ca/lineup/topstories.xml', 'cbc'),
		('http://ctvnews.ca/rss/TopStories', 'ctv')]

	for url, name in urls:
		data = {}
		data['items'] = []
		response = requests.get(url)
		soup = BeautifulSoup(response.content, features='xml')
		items = soup.findAll('item')

		for item in items:
			item_json = jsonify_item(item, name)
			data['items'].append(item_json)

		obj = s3.Object(BUCKET_NAME, date + '-' + name + '.json')
		obj.put(Body=json.dumps(data))

	return

def jsonify_item(item, news_outlet):
	json = {}
	json['guid'] = item.guid.text
	json['title'] = item.title.text
	json['link'] = item.link.text
	json['pubDate'] = parse_date(item.pubDate.text, news_outlet)
	json['description'] = item.description.text
	return json

def parse_date(date, news_outlet):
	if news_outlet == 'cbc' or news_outlet == 'thestar':
		date = datetime.strptime(date[:-4], '%a, %d %b %Y %H:%M:%S')

	if news_outlet == 'ctv':
		date = datetime.strptime(date[:-6], '%a, %d %b %Y %H:%M:%S')

	return date.strftime("%Y/%m/%d %H:%M:%S")

def main():
	rss_to_bucket()

if __name__ == '__main__':
	main()