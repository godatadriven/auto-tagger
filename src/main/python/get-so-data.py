#!/usr/bin/env python

import requests
import json
from readability import readability
from time import sleep

stackoverflow_api_key = 'Tr1x)VLjLE4RCc*Zk0wuAA(('
questions_per_tag = 10000
item_delimiter = '' #empty for very first item

def handle_potential_backoff_response(api_response_json):
  if ('backoff' in api_response_json):
    backoff_seconds = api_response_json['backoff']
    print 'Backing off for ' + str(backoff_seconds) + ' seconds ...'
    sleep(backoff_seconds)

def stream_tag_questions_to_file(tag, questions_data_file):
  questions_received = 0
  page = 1
  global item_delimiter

  while (questions_received < questions_per_tag):
    params = {
      'key':stackoverflow_api_key,
      'page':page,
      'pagesize':100,
      'order':'desc',
      'sort':'creation',
      'tagged':tag,
      'site':'stackoverflow',
      'filter':'!)svnmEb0nvQYygI7ywjg'
    }

    print 'Getting questions for tag ' + tag + ', params = ' + str(params)
    questions_response = requests.get(questions_api_url, params=params)

    if questions_response.ok:
      for question in questions_response.json()['items']:
        question_data_file.write(item_delimiter + json.dumps(question, indent=4, sort_keys=True))
        item_delimiter = ',\n'

      handle_potential_backoff_response(questions_response.json())

    if questions_response.json()['has_more']:
      questions_received = questions_received + 100
      page = page + 1
    else:
      break

tags_api_url = 'http://api.stackexchange.com/2.2/tags'
tags_api_get_params = {
  'key':stackoverflow_api_key,
  'pagesize':23,
  'order':'desc',
  'sort':'popular',
  'site':'stackoverflow'
}

top_23_tags_response = requests.get(tags_api_url, params=tags_api_get_params)

if top_23_tags_response.ok:
  tags = [tag_item['name'] for tag_item in top_23_tags_response.json()['items']]

# to make certain people happy:
tags = tags + [u'clojure', u'scala']

questions_api_url = 'http://api.stackexchange.com/2.2/questions'

with open('question_data.json', 'w') as question_data_file:
  question_data_file.write('{"questions":[')

  for tag in tags:
    stream_tag_questions_to_file(tag, question_data_file)

  question_data_file.write(']}')

