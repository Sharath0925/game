from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  # Update if needed
db = client['memory_game']
high_scores_collection = db['high_scores']
users_collection = db['users']
