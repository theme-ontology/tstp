#: define (my)sql dbs here
#: this file should be copied to credentials.py and edited

DBS = {
	'tstp@dreamhost' : dict(
		host = 'sql.thestartrekproject.net',
		db = 'thestartrekproject_master',
		user = '',
		password = '',
	),
	
	'tstp@aws' : dict(
		host = '127.0.0.1',
		db = 'theme_ontology_web',
		user = '',
		password = '',
	),
	
}

#: "tstp" will be used by the web 
DBS['tstp'] = DBS['tstp@dreamhost']


#: the url used to test this deployment, must end with /
SERVER_URL = "http://127.0.0.1/tstp/webui/"

#: where is the theming git repository located?
GIT_THEMING_PATH = "f:\\theming"

