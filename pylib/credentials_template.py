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

#: where is the theming git repository located?
GIT_THEMING_PATH = "c:\\repos\\theming"
GIT_THEMING_PATH_HIST = "c:\\repos\\theming-hist"

#: public directory
PUBLIC_DIR = "f:\\www\\pub"


