import requests
import os
import jwt as jwtToken
from google.auth import jwt

from mongo import get_database_client, get_database
from dotenv import load_dotenv
from services.auth_service import verify_auth_token
from services.client_service import google_ads_client as get_google_ads_client

load_dotenv()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

def generate_token_and_jwt(auth_data: dict):
    try:

        print("Generating Auth Token- ", auth_data)
        code = auth_data.get("code")
        print(code)

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if not all([code]):
            return {"message": "Incomplete authentication data"}

        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code"
        }

        response = requests.post("https://oauth2.googleapis.com/token", data=payload)
        response_data = response.json()
        print(response_data)

        if "error" in response_data:
            return {"error": response_data["error"], "error_description": response_data.get("error_description")}

        access_token = response_data.get("access_token")
        id_token = response_data.get("id_token")

        if not id_token:
            return {"error": "No ID token found"}

        # Decode ID token
        decoded_token = jwt.decode(id_token , verify=False)

        # Store data in MongoDB
        mongo_client = get_database_client()
        db = get_database(mongo_client, MONGO_DB_NAME)
        collection = db["users"]

        user_data = {
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "domain": decoded_token.get("hd"),
            "email": decoded_token.get("email").lower(),
            "client_secret": client_secret,
            "client_id": client_id,
            "refresh_token": response_data.get("refresh_token")
        }
        print("User Data- ", user_data)

        # Define filter based on email address
        filter_criteria = {"email": user_data["email"]}

        update_operation = {"$set": user_data}

        # Perform upsert operation
        collection.update_one(filter_criteria, update_operation, upsert=True)

        # Generate JWT token
        encoded_jwt = jwtToken.encode({"email": user_data["email"]}, os.getenv("JWT_SECRET"), algorithm="HS256")
        print("JWT Token- ", encoded_jwt)

        return {
            "message": "User Login successfully",
            "data": {
                "token": encoded_jwt,
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data["picture"],
                "domain": user_data["domain"]
            }
        }

    except Exception as e:
        return {"error": str(e)}


def access_token_login (auth_data: dict):
    try:
        print("Access Token Login- ", auth_data)
        access_token = auth_data.get("access_token")
        if not access_token:
            return {"message": "Incomplete authentication data"}

        # Decode ID token
        decoded_token = jwt.decode(access_token, verify=False)

        # Store data in MongoDB
        mongo_client = get_database_client()
        db = get_database(mongo_client, MONGO_DB_NAME)
        collection = db["users"]

        email = decoded_token.get("email").lower()
        user_data = collection.find_one({"email": email})
        if not user_data:
            return {"error": "User not found"}

        return {
            "message": "User Login successfully",
            "data": {
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data["picture"],
                "domain": user_data["domain"]
            }
        }

    except Exception as e:
        return {"error": str(e)}


def get_linked_accounts(auth_data: dict):
    try:
        print("Access Token Login- ", auth_data)
        email = auth_data.get("email")
        if not email:
            return {"message": "Incomplete authentication data"}

        # Retrieve user from MongoDB
        mongo_client = get_database_client()
        db = get_database(mongo_client, MONGO_DB_NAME)
        collection = db["users"]
        user = collection.find_one({"email": email})
        if not user:
            return {"error": "User not found"}

        # Get Access Token
        token_url = "https://www.googleapis.com/oauth2/v3/token"
        token_data = {
            "client_id": user["client_id"],
            "client_secret": user["client_secret"],
            "refresh_token": user["refresh_token"],
            "grant_type": "refresh_token"
        }
        response = requests.post(token_url, data=token_data)
        if response.status_code != 200:
            return {"error": "Failed to obtain access token"}

        access_token = response.json().get("access_token")
        if not access_token:
            return {"error": "Access token not found in response"}

        print("Access Token- ", access_token)

        # Make request to Google Ads API to list accessible customers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": os.getenv("DEVELOPER_TOKEN")
        }

        response = requests.get(
            "https://googleads.googleapis.com/v16/customers:listAccessibleCustomers",
            headers=headers
        )

        # Handle response
        if response.status_code != 200:
            return {"error": "Failed to list accessible customers"}

        # Parse response data and return
        data = response.json()
        return {
            "message": "Accessible customers retrieved successfully",
            "data": data
        }

    except Exception as e:
        return {"error": str(e)}
