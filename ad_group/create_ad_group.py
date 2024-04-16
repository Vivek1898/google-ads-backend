from google_adverts.configuration import GoogleAds
from exception.handle_google_ads_exception import handle_google_ads_exception
from google.ads.googleads.errors import GoogleAdsException

def create_ad_grp(google_ads_client, camp_data):
    try:
        print("Here to create a ad group for given data2 - ")
        print(google_ads_client, camp_data)
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
        return ad_group_id
    except GoogleAdsException as ex:
        handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None



