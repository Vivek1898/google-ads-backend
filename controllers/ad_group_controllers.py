# Description: Ad Group controllers to create and list ad groups for a campaign
from google.ads.googleads.errors import GoogleAdsException
from services.auth_service import verify_auth_token
from services.client_service import google_ads_client as get_google_ads_client
from exception.handle_google_ads_exception import handle_google_ads_exception




def create_ad_group (request, camp_data):
    try:
        print("Here to create a ad group for given data2 - ")
        print(request, camp_data)
        user = verify_auth_token(request)
        if(user == False):
            return {"error": "Please login to access this resource"}
        print(user)
        google_ads_client = get_google_ads_client(user, camp_data)

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
        return handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None


def list_ad_groups(request, camp_data):
    try:
        print("Here to list ad groups for given data2 - ")
        print(request, camp_data)
        user = verify_auth_token(request)
        if(user == False):
            return {"error": "Please login to access this resource"}
        print(user)

        google_ads_client = get_google_ads_client(user, camp_data)

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
        return handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None

