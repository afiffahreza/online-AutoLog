import requests, os

class CouchDB:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.debug = os.environ.get('DEBUG', 0)

    def create_db(self, db_name):
        response = self.session.put(f'{self.url}/{db_name}')
        if response.status_code == 201:
            if self.debug:
                print(f'Database {db_name} created')
        elif response.status_code == 412:
            print(f'Database {db_name} already exists')
        else:
            print(f'Error creating database {db_name}: {response.status_code}')

    def delete_db(self, db_name):
        response = self.session.delete(f'{self.url}/{db_name}')
        if response.status_code == 200:
            if self.debug:
                print(f'Database {db_name} deleted')
        else:
            print(f'Error deleting database {db_name}: {response.status_code}')

    def insert(self, db_name, doc_id, data):
        response = self.session.put(f'{self.url}/{db_name}/{doc_id}', json=data)
        if response.status_code == 201:
            if self.debug:
                print(f'Document {data} inserted')
        else:
            print(f'Error inserting document {data}: {response.status_code}')

    def get(self, db_name, doc_id):
        response = self.session.get(f'{self.url}/{db_name}/{doc_id}')
        if response.status_code == 200:
            if self.debug:
                print(f'Document {doc_id} retrieved')
            return response.json()
        else:
            print(f'Error retrieving document {doc_id}: {response.status_code}')

    def get_last(self, db_name):
        response = self.session.get(f'{self.url}/{db_name}/_all_docs')
        if response.status_code == 200:
            if self.debug:
                print(f'Last document retrieved')
            response = self.session.get(f'{self.url}/{db_name}/{response.json()["rows"][-1]["id"]}')
            if response.status_code == 200:
                return response.json()
            else:
                print(f'Error retrieving last document: {response.status_code}')
        else:
            print(f'Error retrieving last document: {response.status_code}')

    def delete(self, db_name, doc_id, rev):
        response = self.session.delete(f'{self.url}/{db_name}/{doc_id}?rev={rev}')
        if response.status_code == 200:
            if self.debug:
                print(f'Document {doc_id} deleted')
        else:
            print(f'Error deleting document {doc_id}: {response.status_code}')

    def update(self, db_name, doc_id, rev, data):
        response = self.session.put(f'{self.url}/{db_name}/{doc_id}?rev={rev}', json=data)
        if response.status_code == 201:
            if self.debug:
                print(f'Document {doc_id} updated')
        else:
            print(f'Error updating document {doc_id}: {response.status_code}')
    
    def get_docs_count(self, db_name):
        response = self.session.get(f'{self.url}/{db_name}/_all_docs')
        if response.status_code == 200:
            return len(response.json()['rows'])
        else:
            print(f'Error getting documents count: {response.status_code}')
