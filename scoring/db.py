import couchdb
import os

couchdb_url = os.environ.get('COUCHDB_URL', 'http://admin:password@localhost:5984')

db = couchdb.Server(couchdb_url)

