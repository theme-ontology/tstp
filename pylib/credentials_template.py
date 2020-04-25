#: define (my)sql dbs and local paths here
#: this file should be copied to credentials.py and edited

DBS = {
	'tstp@aws' : dict(
		host = '127.0.0.1',
		db = 'theme_ontology_web',
		user = '',
		password = '',
	),
	'tstp@ldnhome' : dict(
		host = '127.0.0.1',
		db = 'theme_ontology_web',
		user = '',
		password = '',
	),
}

#: "tstp" will be used by the web scripts
DBS['tstp'] = DBS['tstp@aws']

#: the url used to test this deployment, must end with /
SERVER_URL = "http://127.0.0.1/tstp/webui/"
SERVER_PUB_URL = "http://127.0.0.1/pub/"

#: where is the theming git repository located?
GIT_THEMING_PATH = "c:\\repos\\theming"
GIT_THEMING_PATH_HIST = "c:\\repos\\theming-hist"
GIT_THEMING_PATH_M4 = "c:\\repos\\theming-m4"

#: public directory
PUBLIC_DIR = "f:\\www\\pub"

#: Apache Solr server URL base, must end with /
SOLR_URL = "http://localhost:8983/solr/"

#: where to keep temporary data files (useful for debugging)
import tempfile
TEMP_PATH = tempfile.gettempdir()

#: email distribution
EMAIL_ADMIN = [
	"example@foo.bar",
]

#: how to post to slack
SLACK_WEBHOOK_URL = None
