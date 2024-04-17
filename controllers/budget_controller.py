import os
from http.client import HTTPException
from exception.handle_google_ads_exception import handle_google_ads_exception

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from mongo import get_database_client, get_database
from ad_group.create_ad_group import create_ad_grp
from ad.create_ad import create_advert
from exception.handle_google_ads_exception import handle_google_ads_exception
from keywords.add_keywords import add_keywords_in_ad_group
import argparse
import datetime
import sys
import uuid
from middlewares.middlewares import decode_token
import requests
from services.auth_service import verify_auth_token
from services.client_service import google_ads_client as google_ads_client
from dotenv import load_dotenv
load_dotenv()

def create_budget(request, budget_data):
    # Create a budget, which can be shared by multiple campaigns.
    user = verify_auth_token(request)
    if user == False:
        return {"error": "Please login to access this resource"}
    print(user)

    client = google_ads_client(user, budget_data)

    # Extract budget data from budget_data dictionary
    budget_name = budget_data.get("name", f"Interplanetary Budget {uuid.uuid4()}")
    delivery_method = budget_data.get("delivery_method", "STANDARD")
    amount_micros = budget_data.get("amount_micros", 500000)
    customer_id = budget_data.get("customer_id")

    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = budget_name
    campaign_budget.delivery_method = delivery_method
    campaign_budget.amount_micros = amount_micros

    campaign_budget_service = client.get_service("CampaignBudgetService")
    # Add budget.
    try:
        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
        print(f"Created campaign budget {campaign_budget_response.results[0].resource_name}.")
        return {
            "message": "Campaign budget created successfully",
            "data": {
                "resource_name": campaign_budget_response.results[0].resource_name,
                "name": budget_name,
                "delivery_method": delivery_method,
                "amount_micros": amount_micros
            }
        }

    except GoogleAdsException as ex:
        # return status code 500 if an error occurs
       return handle_google_ads_exception(ex)

def list_budgets(request, budget_data):
    user = verify_auth_token(request)
    if user == False:
        return {"error": "Please login to access this resource"}
    print(user)

    client = google_ads_client(user, budget_data)

    customer_id = budget_data.get("customer_id")
    query = "SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros, campaign_budget.delivery_method FROM campaign_budget"
    ga_service = client.get_service("GoogleAdsService")
    response = ga_service.search(customer_id=customer_id, query=query)

    payload = []
    for row in response:
        payload.append({
            "id": row.campaign_budget.id,
            "name": row.campaign_budget.name,
            "amount_micros": row.campaign_budget.amount_micros,
            "delivery_method": row.campaign_budget.delivery_method
        })

    return {
        "message": "Budgets fetched successfully",
        "data": payload
    }