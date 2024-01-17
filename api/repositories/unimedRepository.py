from api.database import get_database

class UnimedRepository:
    # def __init__(self):
    #     dbname = get_database()
    
    def insert_many(data):
        dbname = get_database()
        collection_name = dbname["unimed"]
        collection_name.insert_many(data)

    def insert_one(data):
        dbname = get_database()
        collection_name = dbname["unimed"]
        collection_name.insert_one(data)

    def find_dentistas():
        dbname = get_database()
        collection_name = dbname["unimed"]
        return collection_name.find()
    
    def find_dentista(cro_num, cro_uf):
        dbname = get_database()
        collection_name = dbname["unimed"]
        return collection_name.find({"cro": cro_num, "uf_cro": cro_uf})
