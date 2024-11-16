from pymongo import MongoClient
from django.conf import settings

def get_db_handle(db_name=settings.MONGO_DB_NAME, 
                  host=settings.MONGO_DB_HOST, 
                  port=settings.MONGO_DB_PORT, 
                  username=settings.MONGO_DB_USERNAME, 
                  password=settings.MONGO_DB_PASSWORD):
    client = MongoClient(host=host, port=port, username=username, password=password)
    db_handle = client[db_name]
    return db_handle, client
