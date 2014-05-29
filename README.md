auto-tagger
===========

Text classifier that suggests tags for Stackoverflow questions.

## Requirements, Assumptions

This software has been tested on a relatively clean Mac OS (10.9.3), with the following components installed:

* Python 2.7
* Node.js/npm (0.10/1.4)

If not available, the easiest way to obtain these is using [Homebrew](http://brew.sh/).

For the front-end, we'll need the [Bower package manager](http://bower.io/), which can be installed with `npm install -g bower`.

## Additional Installation

The project depends on several Python and front-end packages, as well as a locally running Solr server. These can be obtained as follows:

1. `pip install -r requirements.txt` -- you may want to install these packages into a Python virtualenv for this project,
2. `cd src/main/python/static/` and `bower install` will download all front-end dependencies into a `bower_components` directory,
3. `brew install solr` will install the Solr server. If not using Homebrew, Solr can be installed manually from [Apache](http://lucene.apache.org/solr/);

## Getting Stackoverflow questions into Solr

The project contains a script for downloading questions from the Stackoverflow api. Running 

```
python get-so-data.py
```

from `src/main/python` will download the questions into a file `question_data.json`. Currently, the download will consist of 250k questions and may take up to 1 hr. To modify the download size, you can change the value of `questions_per_tag` in the script.

Once the download is finished, it's time to start Solr. Solr requires a directory for reading its configuration and writing its data. In this case, it should be the absolute path pointing to the `src/main/solr-config` directory inside of this project. As such, starting Solr should look as 

```
solr [absolute_path_to_auto_tagger_project]/src/main/solr-config
```

Confirm that Solr is running by checking http://localhost:8983/solr/.

Finally, the questions should be loaded into Solr by running 

```
python load_questions.py question_data.json
```

For 250k questions, this should run without (excessive) swapping on a fairly modern system with 8Gb RAM available. Confirm that the questions are loaded by going to the solr admin page, selecting the collection "stackoverflow-collection", and checking the number of documents in the "statistics" pane. The number of documents will actually be smaller than 250k because of duplicate questions with overlapping tags.

## Running the classifier

The classifier can be started with 

```
python classifier_app.py
```

Open a browser pointing to http://localhost:5000/static/predict.html and start typing some hypothetical questions...