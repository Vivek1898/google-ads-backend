# app/controllers/campaign_controller.py
import os
from http.client import HTTPException
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from mongo import get_database_client, get_database
from exception.handle_google_ads_exception import handle_google_ads_exception
import datetime
import sys
import uuid
from middlewares.middlewares import decode_token
from services.auth_service import verify_auth_token
from services.client_service import google_ads_client
import requests
from dotenv import load_dotenv

load_dotenv()

_DATE_FORMAT = "%Y%m%d"
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


async def get_campaigns(request, camp_data):
    # Implement logic to retrieve campaigns from the Google Ads API
    user = verify_auth_token(request)
    if (user == False):
        return {"error": "Please login to access this resource"}
    print(user)
    client = google_ads_client(user, camp_data)
    ga_service = client.get_service("GoogleAdsService")
    print(ga_service)
    query = (
        f"SELECT "
        f"campaign.id, "
        f"campaign.name, "
        f"campaign.status, "
        f"campaign.start_date, "  # Include start date field
        f"campaign.end_date, "    # Include end date field
        f"campaign.advertising_channel_type, "
        f"campaign.resource_name, "
        f"campaign.network_settings.target_google_search, "
        f"campaign.network_settings.target_search_network, "
        f"campaign.network_settings.target_content_network, "
        f"campaign_budget.amount_micros, "
        f"campaign.optimization_score, "
        f"metrics.impressions, "
        f"metrics.ctr, "
        f"metrics.cost_micros, "
        f"metrics.clicks, "
        f"metrics.average_cpc "
        f"FROM campaign "
    )
    response = ga_service.search(customer_id=camp_data['customer_id'], query=query)
    payload = []
    for row in response:
        # print(f"Campaign with ID {row.campaign.id} and name {row.campaign.name}")
        payload.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status,
            "campaign_budget": row.campaign_budget.amount_micros,
            "optimization_score": row.campaign.optimization_score,
            "impressions": row.metrics.impressions,
            "ctr": row.metrics.ctr,
            "cost_micros": row.metrics.cost_micros,
            "clicks": row.metrics.clicks,
            "average_cpc": row.metrics.average_cpc,
            "start_date": row.campaign.start_date,
            "end_date": row.campaign.end_date,
            "advertising_channel": row.campaign.advertising_channel_type,
            "target_google_search": row.campaign.network_settings.target_google_search,
            "target_search_network": row.campaign.network_settings.target_search_network,
            "target_content_network": row.campaign.network_settings.target_content_network,
            "resource_name": row.campaign.resource_name,
                        })

    return payload


def create_campaigns(request, camp_data):
    user = verify_auth_token(request)
    if (user == False):
        return {"error": "Please login to access this resource"}
    print(user)
    client = google_ads_client(user, camp_data)
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_service = client.get_service("CampaignService")
    customer_id = camp_data.get("customer_id")

    # Create a budget, which can be shared by multiple campaigns.
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = camp_data.get("budget_name", f"Interplanetary Budget {uuid.uuid4()}")
    campaign_budget.delivery_method = camp_data.get("budget_delivery_method",
                                                    client.enums.BudgetDeliveryMethodEnum.STANDARD)
    campaign_budget.amount_micros = camp_data.get("budget_amount_micros", 500000)
    # check if budget already exists

    # Add budget.
    print("Creating campaign budget")
    try:
        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
    except GoogleAdsException as ex:
        print('Exception in creating campaign budget')
        return handle_google_ads_exception(ex)
    print(f"Created campaign budget {campaign_budget_response.results[0].resource_name}.")

    # Create campaign.
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = camp_data.get("campaign_name", f"Interplanetary Cruise {uuid.uuid4()}")
    campaign.advertising_channel_type = camp_data.get("advertising_channel_type",
                                                      client.enums.AdvertisingChannelTypeEnum.SEARCH)

    # Recommendation: Set the campaign to PAUSED when creating it to prevent
    # the ads from immediately serving. Set to ENABLED once you've added
    # targeting and the ads are ready to serve.
    campaign.status = camp_data.get("campaign_status", client.enums.CampaignStatusEnum.PAUSED)

    # Set the bidding strategy and budget.
    campaign.manual_cpc.enhanced_cpc_enabled = True
    campaign.campaign_budget = campaign_budget_response.results[0].resource_name

    # Set the campaign network options.
    campaign.network_settings.target_google_search = camp_data.get("target_google_search", True)
    campaign.network_settings.target_search_network = camp_data.get("target_search_network", True)
    campaign.network_settings.target_partner_search_network = camp_data.get("target_partner_search_network", False)
    campaign.network_settings.target_content_network = camp_data.get("target_content_network", True)

    # Optional: Set the start date.
    start_time = datetime.date.today() + datetime.timedelta(days=1)
    campaign.start_date = start_time.strftime(_DATE_FORMAT)

    # Optional: Set the end date.
    end_time = start_time + datetime.timedelta(weeks=4)
    campaign.end_date = end_time.strftime(_DATE_FORMAT)

    # Add the campaign.
    try:
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        print(f"Created campaign {campaign_response.results[0].resource_name}.")
        return {
            "created_campaign": campaign_response.results[0].resource_name,
        }
    except GoogleAdsException as ex:
       return handle_google_ads_exception(ex)


def get_campaigns_details(request, camp_data):
    user = verify_auth_token(request)
    if (user == False):
        return {"error": "Please login to access this resource"}
    print(user)
    client = google_ads_client(user, camp_data)
    ga_service = client.get_service("GoogleAdsService")
    query = (
        f"SELECT "
        f"campaign.id, "
        f"campaign.name, "
        f"campaign.status, "
        f"campaign.start_date, "  # Include start date field
        f"campaign.end_date, "    # Include end date field
        f"campaign.advertising_channel_type, "
        f"campaign.resource_name, "
        f"campaign.network_settings.target_google_search, "
        f"campaign.network_settings.target_search_network, "
        f"campaign.network_settings.target_content_network, "
        f"campaign_budget.amount_micros, "
        f"campaign.optimization_score, "
        f"metrics.impressions, "
        f"metrics.ctr, "
        f"metrics.cost_micros, "
        f"metrics.clicks, "
        f"metrics.average_cpc "
        f"FROM campaign "
        f"WHERE campaign.id = {camp_data['campaign_id']}"
    )


    response = ga_service.search(customer_id=camp_data['customer_id'], query=query)

    result = []
    for row in response:
        result.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status,
            "campaign_budget": row.campaign_budget.amount_micros,
            "optimization_score": row.campaign.optimization_score,
            "impressions": row.metrics.impressions,
            "ctr": row.metrics.ctr,
            "cost_micros": row.metrics.cost_micros,
            "clicks": row.metrics.clicks,
            "average_cpc": row.metrics.average_cpc,
            "start_date": row.campaign.start_date,
            "end_date": row.campaign.end_date,
            "advertising_channel": row.campaign.advertising_channel_type,
            "target_google_search": row.campaign.network_settings.target_google_search,
            "target_search_network": row.campaign.network_settings.target_search_network,
            "target_content_network": row.campaign.network_settings.target_content_network,
            "resource_name": row.campaign.resource_name,
        })


    print(response)

    return {
            "message": "Campaign details fetched successfully",
            "campaign_details": result,
        }


