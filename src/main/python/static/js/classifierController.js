var classifierApp = angular.module('classifier', ['ngSanitize']).config(['$locationProvider', function($locationProvider){$locationProvider.html5Mode(true)}]);

classifierApp.directive('dynamic', function($compile) {
	return {
		restrict : 'A',
		replace : true,
		link : function(scope, ele, attrs) {
			scope.$watch(attrs.dynamic, function(html) {
				ele.html(html);
				$compile(ele.contents())(scope);
			});
		}
	};
});

classifierApp.controller('ClassifierCtrl', function ClassifierCtrl($scope, $http, $location) {
	$scope.wordCount = 0;

	$scope.predict = function() {
		$http.get('/classify/'+ $scope.predict.query).error(function(error) {
			$scope.msg = error
		}).success(function(data) {
			console.log(data)
			$scope.docs = null
			$scope.predictions = data['label_predictions']
			$scope.prediction_n_docs = data['docs'].length
			$scope.classified_docs = data['docs']
			$scope.aggregated_explanations = data['aggregated_explanation']
			$scope.zoomed_doc = null
			$scope.predict.highlighted_query = null
		});
	}

	$scope.predictOnNewOrRemovedWord = function($event) {
		console.log($event.keyCode);
		currentWordCount = $scope.predict.query.split(" ").length;

		if (currentWordCount < $scope.wordCount || $event.keyCode === 32) {
			$scope.predict();
			$scope.wordCount = currentWordCount;
		}
	}

	$scope.show_predictions = function() {
		return $scope.predictions != null && Object.keys($scope.predictions).length > 0
	}
	
	$scope.explain_category = function(label) {
		$scope.predict.highlighted_query = explain_highlight($scope.aggregated_explanations[label])
	}

	$scope.explain = function() {
		$scope.docs = $scope.classified_docs
	}

	$scope.zoom = function(doc) {
		$scope.zoomed_doc = doc
		$scope.predict.highlighted_query = explain_highlight(doc['explanation'])
		$('.alert').show()
	}

	$scope.close_details = function() {
		$('.alert').hide()
	}

	$scope.init = function() {
		doc_id = ($location.search()).key

		if (doc_id) {
			$http.get('/doc/'+ doc_id).error(function(error) {
				$scope.msg = error
			}).success(function(data) {
				$scope.predict.query = data[0]['text']
				$scope.predict()
			});
		}

	}

	explain_highlight = function(wordlist) {
		query_text = $scope.predict.query
		for (word in wordlist) {
			val = wordlist[word] + 0.1
			textcolor = 'color:rgba(0,0,0,1);'
			//replace found word with a <span background-color=rgba(0,255,0, val)>word</span>
			r = new RegExp('\\b('+word+')\\b', 'gi')
			if (val > 0.6) {
				textcolor = 'color:rgba(255,255,255,1);'
			}
			query_text = query_text.replace(r, '<span style="'+textcolor+'background-color:rgba(45,108,162,'+val+');border-radius:4px;padding:2px">$1</span>')
		}
		return query_text
	}

	endsWithSpace = function(str) {
		return str.substr(str.length - 1, str.length) === " ";
	}

});
