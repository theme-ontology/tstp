#: define (my)sql dbs and local paths here
#: this file should be copied to credentials.py and edited

DBS = {
	'tstp@ldnhome' : dict(
		host = 'mysql',
		db = 'tstpdockerdb',
		user = 'tstpdockeruser',
		password = 'tstpdockerpass',
	),
}

DBS['tstp'] = DBS['tstp@ldnhome']

#: the url used to test this deployment, must end with /
#: (should deprecate and get rid of these!)
SERVER_URL = "/"
SERVER_PUB_URL = "/pub/"

#: where is the theming git repository located?
GIT_THEMING_PATH = "/code/theming"
GIT_THEMING_PATH_HIST = "/code/theming-hist"
GIT_THEMING_PATH_M4 = "/code/theming-m4"

#: public directory
PUBLIC_DIR = "/www/pub"

#: Apache Solr server URL base, must end with /
SOLR_URL = "http://localhost:8983/solr/"

#: Elasticsearch server if available
ES_HOSTS = [{'host': 'es01', 'port': 9200}]

#: where to keep temporary data files (useful for debugging)
import tempfile
TEMP_PATH = tempfile.gettempdir()

#: email distribution
EMAIL_ADMIN = [
	"mikael@odinlake.net",
]

#: how to post to slack
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

