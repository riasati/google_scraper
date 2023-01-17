class DataBase:
    def __init__(self, collection_name):
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017")
        db = client.google
        self.collection = db[collection_name]

    def get_collection_data(self, query, num, page):
        documents = self.collection.find({"query": query}).limit(num).skip((page - 1) * num)
        return [doc for doc in documents]

    def add_documents(self, document_list):
        self.collection.insert_many(document_list)