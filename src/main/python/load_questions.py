import pysolr
import json
import sys

solr = pysolr.Solr('http://localhost:8983/solr/stackoverflow-collection')
questions_file = open(sys.argv[1], 'r')
questions = json.loads(questions_file.read())['questions']
solr.add(questions)
