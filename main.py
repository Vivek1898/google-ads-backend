# main.py

from fastapi import FastAPI
from routes.campaign_routes import router as campaign_router
from routes.auth_routes import router as auth_router
from routes.ad_group_route import router as ad_group_router
from routes.budget_route import router as budget_router
from routes.ad_router import router as ad_router
from mongo import get_database_client, get_database
from middlewares.middlewares import auth_middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

# set header for the application


# MongoDB settings
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Set CORS policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# app.middleware("http")(auth_middleware)


# Establish MongoDB connection
mongo_client = get_database_client()
mongo_db = get_database(mongo_client, MONGO_DB_NAME)

# Mount routers
app.include_router(campaign_router, prefix="/api/v1", tags=["campaigns"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(ad_group_router, prefix="/api/v1", tags=["adGroup"])
app.include_router(budget_router, prefix="/api/v1", tags=["budget"])
app.include_router(ad_router, prefix="/api/v1", tags=["ad"])

