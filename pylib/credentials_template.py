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

