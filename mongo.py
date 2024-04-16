# mongo.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_DB_URL")

# Function to establish MongoDB connection
def get_database_client():
    return MongoClient(MONGO_URI)

# Function to get the MongoDB database
def get_database(client, database_name):
    return client[database_name]
