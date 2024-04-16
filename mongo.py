# mongo.py

from pymongo import MongoClient

# MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"

# Function to establish MongoDB connection
def get_database_client():
    return MongoClient(MONGO_URI)

# Function to get the MongoDB database
def get_database(client, database_name):
    return client[database_name]
