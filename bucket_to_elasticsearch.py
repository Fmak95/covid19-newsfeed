'''
	Get Data from S3 and put into ElasticSearch
'''
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from settings import BUCKET_NAME, NEWS_OUTLETS
import boto3
import pdb
from time import gmtime, strftime
import json
import hashlib
import os

def main():
	date = strftime("%Y-%m-%d", gmtime())
	index_names = [date + '-' + name for name in NEWS_OUTLETS]
	es = Elasticsearch(os.environ['ES_URL'])
	# es = Elasticsearch()

	for index_name in index_names:
		data = get_data_from_s3(index_name)
		create_index(es, index_name)
		index_news(es, data, index_name)

def index_news(es, data, index_name):
	def gen_data():
		for news in data:
			body = {
				"_op_type": "index",
				"_index": index_name,
				"_id": hashlib.md5(news['link'].encode('utf-8')).hexdigest(), #Hash url and use as primary key
				"_source": {
					'guid': news['guid'],
					'title': news['title'],
					'link': news['link'],
					'pubDate': news['pubDate'],
					'description': news['description']
				}
			}
			yield body
	bulk(es, gen_data())

def create_index(es, index_name):
	if not es.indices.exists(index = index_name):
		es.indices.create(
				index=index_name,
				body={
					'mappings': {
						'properties': {
							'description': {
								'type':'text',
								'analyzer': 'index_analyzer', 
								'fields': {
									'keyword': {'type': 'keyword', 'ignore_above': 256}
								}
							},
							'pubDate':{'type': 'date', "format": "yyyy/MM/dd HH:mm:ss"},
							'link':{
								'type': 'text', 
								'fields': {
									'keyword': {'type': 'keyword', 'ignore_above': 256}
								}
							},
							'title':{
								'type': 'text', 
								'fields': {
									'keyword': {'type': 'keyword', 'ignore_above': 256}
								}
							},
							'guid':{
								'type': 'text', 
								'fields': {
									'keyword': {'type': 'keyword', 'ignore_above': 256}
								}
							},
						}
					},
					'settings': {
						'analysis': {
							'analyzer': {
								'index_analyzer': {
									'type': 'custom',
									'tokenizer': 'standard',
									'char_filter': ['html_strip']
								},
								'query_analyzer': {
										'type': 'custom',
										'tokenizer': 'standard',
										'filter': ['lowercase', 'english_stop']
								}
							},
							'filter': {
								'english_stop': {
									'type': 'stop',
									'stopwords': '_english_'
								}
							}
						}
					},
				},
			)

def get_data_from_s3(index_name):
	s3 = boto3.resource('s3')
	bucket = s3.Bucket(BUCKET_NAME)
	obj = s3.Object(BUCKET_NAME,index_name + '.json')
	data = obj.get()['Body'].read().decode('utf-8')
	data = json.loads(data)
	return data['items']

if __name__ == '__main__':
	main()

