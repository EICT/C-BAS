import eisoil.core.pluginmanager as pm
from mongodatabase import MongoDB
from eisoil.config import (db_ip, db_port, db_name)


def setup():
    mongo_database = MongoDB(db_ip, db_port, db_name)
    pm.registerService('mongodb', mongo_database)