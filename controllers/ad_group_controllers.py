import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from middlewares.middlewares import decode_token
from mongo import get_database_client, get_database


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


def create_ad_group (request, camp_data):
    try:
        print("Here to create a ad group for given data2 - ")
        print(request, camp_data)
        user = verify_auth_token(request)
        if(user == False):
            return {"error": "Invalid or missing token"}
        print(user)
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
            "login_customer_id": camp_data['customer_id'],
        }
        print("Credentials: ", credentials)
        google_ads_client = GoogleAdsClient.load_from_dict(credentials)

        customer_id = str(camp_data["customer_id"])
        campaign_id = str(camp_data["campaign_id"])
        campaign_name = camp_data["name"]
        ad_group_name = campaign_name + " ad group"
        ad_group_service = google_ads_client.get_service("AdGroupService")
        campaign_service = google_ads_client.get_service("CampaignService")

        # Create ad group.
        ad_group_operation = google_ads_client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = ad_group_name
        ad_group.status = google_ads_client.enums.AdGroupStatusEnum.ENABLED
        ad_group.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        ad_group.type_ = google_ads_client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = int(camp_data["ad_budget"])*(10**6)

        # Add the ad group.
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        print(f"Created ad group {ad_group_response}.")
        ad_group_id = None
        # ad_group_id = "156273490729"
        if ad_group_response and ad_group_response.results[0] and ad_group_response.results[0].resource_name:
            ad_group_id = ad_group_response.results[0].resource_name.split('/')[-1]
        return {
            "message": "Ad Group created successfully",
            "data": {
                "ad_group_id": ad_group_id
            }
        }
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None


def list_ad_groups(request, camp_data):
    try:
        print("Here to list ad groups for given data2 - ")
        print(request, camp_data)
        user = verify_auth_token(request)
        if(user == False):
            return {"error": "Invalid or missing token"}
        print(user)
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
            "login_customer_id": camp_data['customer_id'],
        }
        print("Credentials: ", credentials)
        google_ads_client = GoogleAdsClient.load_from_dict(credentials)

        customer_id = str(camp_data["customer_id"])
        campaign_id = str(camp_data["campaign_id"])
        ad_group_service = google_ads_client.get_service("AdGroupService")
        ad_group_query = f"SELECT ad_group.id, ad_group.name FROM ad_group WHERE campaign.id = {campaign_id}"
        ad_group_response = ad_group_service.search(customer_id=customer_id, query=ad_group_query)
        print(f"Ad Groups found: {ad_group_response}")
        return {
            "message": "Ad Groups listed successfully",
            "data": ad_group_response
        }
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None


def handle_googleads_exception(exception):
    # print(exception)
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
    raise exception