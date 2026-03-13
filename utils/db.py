import os
from pymongo import MongoClient

mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db_name = os.environ.get("DB_NAME", "test_assessment_db")
db = client[db_name]

applications_collection = db["applications"]
counsellor_notes_collection = db["counsellor_notes"]
