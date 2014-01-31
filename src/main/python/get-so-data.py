#!/usr/bin/env python

import requests
from readability import readability

tags = ['java', 'scala']
url = 'http://api.stackexchange.com/2.1/questions'

for tag in tags:
  params = {
    'page' : 1,
    'pagesize' : 10, 
    'order' : 'desc',
    'sort' : 'creation',
    'tagged' : tag,
    'site' : 'stackoverflow', 
    'filter' : '!)svnmEb0nvQYygI7ywjg'
  }

  print params
  req = requests.get(url, params=params)

  if req.ok:
    print req.json()
    #params['page'] = 2

print "the end"
