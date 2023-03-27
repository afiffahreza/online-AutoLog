import requests

class CouchDB:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.session.auth = (user, password)

    def create_db(self, db_name):
        response = self.session.put(f'{self.url}/{db_name}')
        if response.status_code == 201:
            print(f'Database {db_name} created')
        elif response.status_code == 412:
            print(f'Database {db_name} already exists')
        else:
            print(f'Error creating database {db_name}: {response.status_code}')

    def insert(self, db_name, doc_id, data):
        response = self.session.put(f'{self.url}/{db_name}/{doc_id}', json=data)
        if response.status_code == 201:
            print(f'Document {data} inserted')
        else:
            print(f'Error inserting document {data}: {response.status_code}')

    def get(self, db_name, doc_id):
        response = self.session.get(f'{self.url}/{db_name}/{doc_id}')
        if response.status_code == 200:
            print(f'Document {doc_id} retrieved')
            return response.json()
        else:
            print(f'Error retrieving document {doc_id}: {response.status_code}')

    def delete(self, db_name, doc_id, rev):
        response = self.session.delete(f'{self.url}/{db_name}/{doc_id}?rev={rev}')
        if response.status_code == 200:
            print(f'Document {doc_id} deleted')
        else:
            print(f'Error deleting document {doc_id}: {response.status_code}')

    def update(self, db_name, doc_id, rev, data):
        response = self.session.put(f'{self.url}/{db_name}/{doc_id}?rev={rev}', json=data)
        if response.status_code == 201:
            print(f'Document {doc_id} updated')
        else:
            print(f'Error updating document {doc_id}: {response.status_code}')
    
    def get_docs_count(self, db_name):
        response = self.session.get(f'{self.url}/{db_name}/_all_docs')
        if response.status_code == 200:
            return len(response.json()['rows'])
        else:
            print(f'Error getting documents count: {response.status_code}')

def input_data(db, app, data):
    # Create database if it doesn't exist
    db.create_db(app)
    # Get how many documents are in the database
    count = db.get_docs_count(app)
    # Insert data document with app as db and count+1 as document and all of the words in the data as json
    db.insert(app, str(count+1), {"data": data})

def get_data(db, app, doc_id):
    res = db.get(app, doc_id)
    return res['data']

def get_all_data(db, app):
    # Get how many documents are in the database
    count = db.get_docs_count(app)
    # Get all documents in the database
    all_data = []
    for i in range(1, count+1):
        res = db.get(app, str(i))
        all_data.append(res['data'])
    return all_data

def get_num_docs(db, app):
    return db.get_docs_count(app)

def input_train(db, app, data):
    # Create database if it doesn't exist with name "train-<app>"
    db.create_db("train-"+app)
    # Get how many documents are in the database
    count = db.get_docs_count("train-"+app)
    # Insert metadata document
    # Metadata attributes:
    # M = number of chunks with the current chunk
    # score = score of the current chunk with M as the number of chunks
    M = data['M']
    score = data['score']
    db.insert(app, str(count+1), {"M": M, "score": score})

def get_train(db, app):
    # Get last document in the database for doc_id
    doc_id = str(db.get_docs_count("train-"+app))
    return db.get("metadata-"+app, doc_id)
