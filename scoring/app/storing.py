# ===== term-count pair to generate baseline score =====
def store_normal_terms(db, app, data: dict):
    # Create database if it doesn't exist
    db.create_db("normal-"+app)
    # Get how many documents are in the database
    count = db.get_docs_count("normal-"+app)
    if not count:
        count = 0
    # Insert data document with app as db and count+1 as document and all of the words in the data as json
    db.insert("normal-"+app, str(count+1), {"data": data})
    print("Stored baseline terms to db")

# ===== normal score database for baseline model =====
def store_normal_score(db, app, data: dict):
    # Create database if it doesn't exist with name "train-<app>"
    db.create_db("train-"+app)
    # Get how many documents are in the database
    count = db.get_docs_count("train-"+app)
    if not count:
        count = 0
    # Insert score document
    db.insert("train-"+app, str(count+1), {"data": data})
    print("Stored baseline score to db")

# ===== term-count pair to generate real time score =====
def store_score(db, app, score: dict):
    # Create database if it doesn't exist with name "score-<app>"
    db.create_db("score-"+app)
    # Get how many documents are in the database
    count = db.get_docs_count("score-"+app)
    if not count:
        count = 0
    # Insert score document
    db.insert("score-"+app, str(count+1), {"data": score})
    print("Stored terms to db")

# ===== Getters =====
    
def get_all_docs(db, db_name):
    docs = []
    num = int(db.get_docs_count(db_name))
    for i in range(1, num+1):
        doc = db.get(db_name, str(i))
        docs.append(doc['data'])
    return docs

def get_normal_terms(db, app):
    # Get tall of the documents in the database
    docs = get_all_docs(db, "normal-"+app)
    # Get the data from the last document
    return docs

def get_normal_scores(db, app):
    # Get tall of the documents in the database
    docs = get_all_docs(db, "train-"+app)
    # Get the score from the last document
    return docs

def get_number_of_termchunks(db, app):
    # Get the number of documents in the database
    count = db.get_docs_count("normal-"+app)
    return count

def get_last_score(db, app):
    last_num = db.get_docs_count("train-"+app)
    # Get the last document in the database
    doc = db.get("score-"+app, str(last_num))
    # Get the score from the last document
    return doc
