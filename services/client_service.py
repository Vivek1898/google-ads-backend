import requests
import os
import jwt as jwtToken
from google.auth import jwt
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from mongo import get_database_client, get_database
from dotenv import load_dotenv
load_dotenv()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

def google_ads_client(user, client_request):
    mongo_client = get_database_client()
    db = get_database(mongo_client, MONGO_DB_NAME)
    collection = db["users"]
    user = collection.find_one({"email": user['email']})
    if not user:
        return {"error": "User not found"}
    print(user)
    credentials = {
        "developer_token": os.getenv("DEVELOPER_TOKEN"),
        "client_id": user["client_id"],
        "client_secret": user["client_secret"],
        "refresh_token": user["refresh_token"],
        "use_proto_plus": "False",
        "login_customer_id": client_request['customer_id'],
    }
    print("Credentials: ", credentials)
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)
    return google_ads_client

