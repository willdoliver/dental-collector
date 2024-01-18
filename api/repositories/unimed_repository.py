from api.database import get_database

class UnimedRepository:
    def __init__(self):
        dbname = get_database()
        self.collection_name = dbname["unimed"]
    
    def insert_many(self, data):
        self.collection_name.insert_many(data)

    def insert_one(self, data):
        self.collection_name.insert_one(data)

    def find_dentistas(self):
        return self.collection_name.find().limit(20)
    
    def find_dentista(self, cro_num, cro_uf):
        return self.collection_name.find({"cro": cro_num, "uf_cro": cro_uf})
