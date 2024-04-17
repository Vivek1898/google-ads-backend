import requests
import os
import jwt as jwtToken
from google.auth import jwt
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from mongo import get_database_client, get_database
from middlewares.middlewares import decode_token
from dotenv import load_dotenv
load_dotenv()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


def verify_auth_token(request):
    token = request
    print(request)
    if token:
        token = token.split("Bearer ")[1] if token.startswith("Bearer ") else token
        print(token)
        payload = decode_token(token)
        print(payload)
        if payload:
            # request.state.user = payload
            return payload
    return False