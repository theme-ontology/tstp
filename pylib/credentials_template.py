#: this file should be copied to credentials.py and edited
from tstp_settings import *
# left for legacy reasons; should be imported directly from tstp_settings going forwards
assert(
	SERVER_URL,
	SERVER_PUB_URL,
	GIT_THEMING_PATH_HIST,
	GIT_THEMING_PATH,
	GIT_THEMING_PATH_M4,
	PUBLIC_DIR,
	TEMP_PATH,
	EMAIL_ADMIN,
)

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

#: Apache Solr server URL base, must end with /
SOLR_URL = "http://localhost:8983/solr/"

#: Elasticsearch server if available
ES_HOSTS = []

#: how to post to slack
SLACK_WEBHOOK_URL = None
