from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_database():
    CONNECTION_STRING = os.getenv("DATABASE_URI")
    client = MongoClient(CONNECTION_STRING)

    return client[os.getenv("DB_NAME")]

if __name__ == "__main__":
    dbname = get_database()