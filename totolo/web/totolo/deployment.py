# Copyright 2023, themeontology.org
# Tests:
import tempfile


TEMP_PATH = tempfile.gettempdir()


class SPHINX:
    HOST = 'sphinx'
    PORT = 9306


class SQLDB:
    HOST = 'sqldb'
    PORT = 5432
    db = 'totolo_db'
    user = 'totolo'
    secret = 'totolo'

