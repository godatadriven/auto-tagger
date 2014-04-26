# _*_ coding: utf-8 _*_

from __future__ import division
import pysolr
import urllib
import re
import numpy as np
from scipy.stats import norm

class KnnClassifier:
  'KNN based classifier on Solr documents'

  classifier_collection = None
  labels = []
  explain = False
  n_search_results = 0
  confidence_cutoff = 0
  word_from_explanation_regexp = re.compile("weight\([\w]*:(.*)\sin\s\d+\).*")

  def __init__(self, k=50, confidence_cutoff=0.7, explain=False):
    self.classifier_collection = pysolr.Solr('http://localhost:8983/solr/stackoverflow-collection', timeout=10)
    self.labels = [label for (label, count) in self.classifier_collection.suggest_terms('tags', '')['tags']]
    self.n_search_results = k
    self.confidence_cutoff = confidence_cutoff
    self.explain = explain

  def get_labels(self):
      return self.labels

  def _normalize_label_confidences(self, labelCounts):
      foundLabels = {label:labelCounts[label] for label in labelCounts if labelCounts[label]['doc_count'] > 0}
      mean_total_score = np.mean([foundLabels[label]['total_lucene_score'] for label in foundLabels])
      std_total_score = np.std([foundLabels[label]['total_lucene_score'] for label in foundLabels])

      for label in foundLabels:
          labelCounts[label]['norm_score'] = round(norm.cdf(labelCounts[label]['total_lucene_score'], loc=mean_total_score, scale=std_total_score), 2)

  def _get_explanation_description(self, explanation, explanation_descriptions):
    description = explanation['description']
    m = self.word_from_explanation_regexp.match(description)
    if m:
      textpart = m.group(1)
      if not textpart in explanation_descriptions:
        explanation_descriptions[textpart] = explanation['value']

  def _search_explanation_description(self, explanation, explanation_descriptions):
    if type(explanation) == dict and explanation.get('details') != None:
      self._get_explanation_details(explanation['details'], explanation_descriptions)

    self._get_explanation_description(explanation, explanation_descriptions)


  def _get_explanation_details(self, explanation, explanation_descriptions):
    for detail in explanation:
      self._search_explanation_description(detail, explanation_descriptions)

  def _normalize_to_percentages(self, word_list):
    percentages = {}
    if len(word_list) > 0:
      vmax = max(word_list.values())
      vmin = min(word_list.values())
      for word in word_list:
        normalized_percentage =  ((word_list[word] - vmin) / (vmin + vmax))
        percentages[word] =  round(normalized_percentage, 2)

    return percentages

  def _get_explanation(self, doc_explanation):
    explanation_texts = {}

    self._search_explanation_description(doc_explanation, explanation_texts)

    return explanation_texts

  def _add_to_aggregated_explanations(self, label, explanation, aggregated_explanations):
    for word in explanation:
      if word in aggregated_explanations[label]:
        aggregated_explanations[label][word] = aggregated_explanations[label][word] + explanation[word]
      else:
        aggregated_explanations[label][word] = explanation[word]


  def classify(self, text):
      labelCounts = {label: {'doc_count':0, 'total_lucene_score':0, 'norm_score':0} for label in self.labels}
      utf8text = unicode(text.encode('utf-8'), errors='ignore')
      firstpartutf8text = ' '.join(utf8text.split()[:1000])
      moreArgs = {
        'rows' : self.n_search_results,
        'defType' : 'edismax',
        'fl' : '*,score',
        'debug' : 'results',
        'debug.explain.structured' : 'true'
      }
      results = self.classifier_collection.search(firstpartutf8text, **moreArgs)

      if self.explain:
          explain = results.debug['explain']

      total_explanation = {label:{} for label in self.labels}

      for result in results:
          for tag in result['tags']:
              if tag in self.labels:
                  labelCounts[tag]['doc_count'] = labelCounts[tag]['doc_count'] + 1
                  labelCounts[tag]['total_lucene_score'] = labelCounts[tag]['total_lucene_score'] + result['score']
                  if self.explain:
                      explanation = self._get_explanation(explain[str(result['question_id'])])
                      self._add_to_aggregated_explanations(tag, explanation, total_explanation)
                      result['explanation'] = self._normalize_to_percentages(explanation)

      self._normalize_label_confidences(labelCounts)
      label_counts_above_cutoff = {label : labelCounts[label] for label in labelCounts if labelCounts[label]['norm_score'] > self.confidence_cutoff}
      if (len(label_counts_above_cutoff) == 0):
          label_counts_above_cutoff = {'UNKNOWN':{'doc_count':0, 'total_lucene_score': 0, 'norm_score':0}}

      labels_sorted_by_confidence = sorted(label_counts_above_cutoff.items(), key = lambda x: x[1]['norm_score'], reverse = True)

      for label in total_explanation:
        # print label
        # print 
        # print
        # print total_explanation[label]
        # print
        # print

        total_explanation[label] = self._normalize_to_percentages(total_explanation[label])


      return {'label_predictions':labels_sorted_by_confidence, 'docs':results.docs, 'agg_explanation':total_explanation}

  