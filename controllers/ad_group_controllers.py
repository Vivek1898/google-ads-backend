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
        user = verify_auth_token(request)
        if (user == False):
            return {"error": "Please login to access this resource"}
        print(user)
        client = get_google_ads_client(user, camp_data)
        ga_service = client.get_service("GoogleAdsService")
        query = (
            f"SELECT "
            f"ad_group.id, "
            f"ad_group.name, "
            f"ad_group.status, "
            f"metrics.clicks, "
            f"metrics.cost_micros, "
            f"metrics.conversions, "
            f"metrics.average_cpc, "
            f"metrics.cost_per_conversion "
            f"FROM ad_group "
            f"WHERE campaign.id = {camp_data['campaign_id']}"
        )

        response = ga_service.search(customer_id=camp_data['customer_id'], query=query)

        result = []
        for row in response:
            result.append({
                "id": row.ad_group.id,
                "name": row.ad_group.name,
                "status": row.ad_group.status,
                "clicks": row.metrics.clicks,
                "cost_micros": row.metrics.cost_micros,
                "conversions": row.metrics.conversions,
                "average_cpc": row.metrics.average_cpc,
                "cost_per_conversion": row.metrics.cost_per_conversion,
            })

        print(response)

        return {
            "message": "Ad  Group list fetched successfully",
            "campaign_details": result,
        }
    except GoogleAdsException as ex:
     return handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
    return None