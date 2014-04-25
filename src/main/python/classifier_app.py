# _*_ coding: utf-8 _*_

from flask import Flask
from classify import KnnClassifier
import json

app = Flask(__name__)
classifier = KnnClassifier(explain=True)

@app.route("/classify/<path:text_to_classify>")
def classify(text_to_classify):
	classifier_result = classifier.classify(text_to_classify)
	predictions = {}
	predictions['label_predictions'] = [{label:prediction} for (label, prediction) in classifier_result['label_predictions']]
	predictions['docs'] = classifier_result['docs']
	predictions['aggregated_explanation'] = classifier_result['agg_explanation']
	return json.dumps(predictions)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)