# main.py

from fastapi import FastAPI
from routes.campaign_routes import router as campaign_router
from routes.auth_routes import router as auth_router
from mongo import get_database_client, get_database
from middlewares.middlewares import auth_middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


app = FastAPI()

# set header for the application


# MongoDB settings
MONGO_DB_NAME = "google_ads_service"
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# app.middleware("http")(auth_middleware)


# Establish MongoDB connection
mongo_client = get_database_client()
mongo_db = get_database(mongo_client, MONGO_DB_NAME)

# Mount routers
app.include_router(campaign_router, prefix="/api/v1", tags=["campaigns"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

