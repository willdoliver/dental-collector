from api.database import get_database
import os

class UnimedRepository:
    def __init__(self):
        self.dbname = get_database()

    def get_collection_name(self, name):
        try:
            return self.dbname[name]
        except:
            return "Database error"

    def insert_many(self, data):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_COLLECTION"))
            collection_name.insert_many(data)
        except:
            return "Database error"

    def insert_dentista(self, data):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_COLLECTION"))
            _id = collection_name.insert_one(data)
            return _id.inserted_id
        except:
            return "Database error"
        
    def update_dentista(self, id, data):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_COLLECTION"))
            updated = collection_name.update_one({"_id": id}, {"$set": data})
            return updated.modified_count
        except Exception as e:
            print(e)
            return "Database error"

    def find_dentistas(self):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_COLLECTION"))
            return collection_name.find().limit(20)
        except:
            return "Database error"

    def find_dentista(self, cro_num, cro_uf):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_COLLECTION"))
            return collection_name.find_one({"cro": cro_num, "uf_cro": cro_uf})
        except Exception as e:
            print(e)
            return "Database error"
        
    def get_urls_crawled(self):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_URLS_COLLECTION"))
            return collection_name.find()
        except:
            return "Database error"

    def save_url_crawled(self, data):
        try:
            collection_name = self.get_collection_name(os.getenv("UNIMED_URLS_COLLECTION"))
            _id = collection_name.insert_one(data)
            return _id.inserted_id
        except:
            return "Database error"

