# Copyright 2023, themeontology.org
# Tests:
import tempfile
import os


TEMP_PATH = tempfile.gettempdir()
IS_MONOLITH = os.getenv("IS_MONOLITH", "1") == "1"


class SPHINX:
    HOST = 'localhost' if IS_MONOLITH else 'sphinx'
    PORT = 9306


class SQLDB:
    HOST = 'localhost' if IS_MONOLITH else 'sqldb'
    PORT = 5432
    db = 'totolo_db'
    user = 'totolo'
    secret = 'totolo'


print("::: {} ::: {} ::: {} :::".format(IS_MONOLITH, SPHINX.HOST, SQLDB.HOST))