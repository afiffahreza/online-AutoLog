import os, requests, json

couchdb_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
couchdb_user = os.environ.get('COUCHDB_USER', 'admin')
couchdb_password = os.environ.get('COUCHDB_PASSWORD', 'password')

terms = ['{"word":"routing","count":90}', '{"word":"thread","count":72}', '{"word":"local","count":339}', '{"word":"asyncexitstack","count":36}', '{"word":"returns","count":17}', '{"word":"traceback","count":17}', '{"word":"server","count":29}', '{"word":"lib","count":339}', '{"word":"customer","count":1152}', '{"word":"peer","count":11}', '{"word":"reading","count":12}', '{"word":"assignment","count":11}', '{"word":"raw","count":18}', '{"word":"put","count":430}', '{"word":"not","count":18}', '{"word":"upstream","count":25}', '{"word":"by","count":11}', '{"word":"threadpool","count":36}', '{"word":"context","count":18}', '{"word":"exceptions","count":36}', '{"word":"protocols","count":17}', '{"word":"limit","count":1}', '{"word":"ignore","count":17}', '{"word":"failed","count":11}', '{"word":"io","count":1697}', '{"word":"recent","count":17}', '{"word":"response","count":48}', '{"word":"range","count":18}', '{"word":"in","count":446}', '{"word":"backends","count":36}', '{"word":"sender","count":18}', '{"word":"fastapi","count":89}', '{"word":"out","count":18}', '{"word":"quantity","count":22}', '{"word":"future","count":18}', '{"word":"handle","count":36}', '{"word":"uvicorn","count":34}', '{"word":"super","count":18}', '{"word":"processed","count":1}', '{"word":"headers","count":17}', '{"word":"http","count":4262}', '{"word":"result","count":35}', '{"word":"path","count":9335}', '{"word":"orders","count":18}', '{"word":"bytes","count":1}', '{"word":"anyio","count":72}', '{"word":"middleware","count":143}', '{"word":"e","count":18}', '{"word":"exc","count":36}', '{"word":"usr","count":339}', '{"word":"scope","count":143}', '{"word":"ok","count":2489}', '{"word":"http4xx","count":81}', '{"word":"values","count":18}', '{"word":"raise","count":54}', '{"word":"site","count":339}', '{"word":"reset","count":11}', '{"word":"request","count":30}', '{"word":"sync","count":72}', '{"word":"app","count":160}', '{"word":"internal","count":17}', '{"word":"py","count":357}', '{"word":"self","count":107}', '{"word":"recv","count":11}', '{"word":"proxy","count":17}', '{"word":"host","count":12}', '{"word":"header","count":12}', '{"word":"retrieved","count":18}', '{"word":"endpoint","count":36}', '{"word":"while","count":12}', '{"word":"index","count":36}', '{"word":"file","count":357}', '{"word":"receive","count":143}', '{"word":"catalog","count":1175}', '{"word":"date","count":1709}', '{"word":"http2xx","count":6023}', '{"word":"function","count":36}', '{"word":"http1xx","count":824}', '{"word":"order","count":1242}', '{"word":"return","count":89}', '{"word":"from","count":12}', '{"word":"send","count":125}', '{"word":"asyncio","count":36}', '{"word":"type","count":17}', '{"word":"list","count":18}', '{"word":"python3","count":339}', '{"word":"error","count":46}', '{"word":"prematurely","count":1}', '{"word":"starlette","count":162}', '{"word":"client","count":12}', '{"word":"asynclib","count":18}', '{"word":"applications","count":35}', '{"word":"asgi","count":34}', '{"word":"of","count":18}', '{"word":"update","count":11}', '{"word":"errors","count":36}', '{"word":"func","count":71}', '{"word":"call","count":231}', '{"word":"concurrency","count":18}', '{"word":"packages","count":339}', '{"word":"delete","count":456}', '{"word":"args","count":36}', '{"word":"impl","count":17}', '{"word":"found","count":18}', '{"word":"kb","count":1}', '{"word":"http5xx","count":63}', '{"word":"connection","count":12}', '{"word":"get","count":2959}', '{"word":"closed","count":1}', '{"word":"indexerror","count":18}', '{"word":"run","count":197}', '{"word":"h11","count":17}', '{"word":"value","count":17}', '{"word":"application","count":17}', '{"word":"worker","count":36}', '{"word":"most","count":17}', '{"word":"total","count":1}', '{"word":"await","count":268}', '{"word":"post","count":420}', '{"word":"k6","count":3394}', '{"word":"route","count":18}', '{"word":"stack","count":18}', '{"word":"info","count":2524}', '{"word":"timestamp","count":5000}', '{"word":"default","count":1697}', '{"word":"id","count":1770}', '{"word":"line","count":358}', '{"word":"ip","count":5966}', '{"word":"number","count":20959}', '{"word":"dependant","count":18}', '{"word":"to","count":36}', '{"word":"last","count":17}', '{"word":"exception","count":17}', '{"word":"https","count":1697}']

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

def jsonize_list(l):
    json_list = []
    for item in l:
        json_list.append(json.loads(item))
    return json_list

def input_data(db, app, data):
    # Create database if it doesn't exist
    db.create_db(app)
    # Get how many documents are in the database
    count = db.get_docs_count(app)
    # Insert data document with app as db and count+1 as document and all of the words in the data as json
    db.insert(app, str(count+1), {"data": jsonize_list(data)})

def get_data(db, app, doc_id):
    return db.get(app, doc_id)


# For testing purposes
# if __name__ == '__main__':
#     db = CouchDB(couchdb_url, couchdb_user, couchdb_password)
#     input_data(db, 'catalog-app', terms)
#     print(get_data(db, 'catalog-app', '1'))