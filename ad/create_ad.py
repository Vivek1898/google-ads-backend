from google_adverts.configuration import GoogleAds
from exception.handle_google_ads_exception import handle_google_ads_exception
from google.ads.googleads.errors import GoogleAdsException

def create_ad_text_asset(google_ads_client, text, pinned_field=None):
    ad_text_asset = google_ads_client.get_type("AdTextAsset")
    ad_text_asset.text = text
    if pinned_field:
        ad_text_asset.pinned_field = pinned_field
    return ad_text_asset

def create_advert(google_ads_client, camp_data):
    try:
        print(google_ads_client, camp_data)
        customer_id = str(camp_data["customer_id"])
        campaign_id = str(camp_data["campaign_id"])
        ad_group_id = str(camp_data["ad_group_id"])
        campaign_name = camp_data["name"]
        ad_group_ad_service = google_ads_client.get_service("AdGroupAdService")
        ad_group_service = google_ads_client.get_service("AdGroupService")

        # Create the ad group ad.
        ad_group_ad_operation = google_ads_client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.status = google_ads_client.enums.AdGroupAdStatusEnum.PAUSED
        ad_group_ad.ad_group = ad_group_service.ad_group_path(
            customer_id, ad_group_id
        )

        # Set responsive search ad info.
        ad_group_ad.ad.final_urls.append(camp_data["final_url"])

        headlines = camp_data["headlines"]
        headlines = headlines.split(',')
        isPinnedHeadLine = True
        pinned_headline = None
        headlines_to_be_added = []
        for headline in headlines:
            if isPinnedHeadLine:
                # Set a pinning to always choose this asset for HEADLINE_1. Pinning is
                # optional; if no pinning is set, then headlines and descriptions will be
                # rotated and the ones that perform best will be used more often.
                served_asset_enum = google_ads_client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
                pinned_headline = create_ad_text_asset(
                    google_ads_client, headline, served_asset_enum
                )
                headlines_to_be_added.append(pinned_headline)
                isPinnedHeadLine = False
            else:
                headlines_to_be_added.append(create_ad_text_asset(google_ads_client, headline))

        ad_group_ad.ad.responsive_search_ad.headlines.extend(headlines_to_be_added)

        descriptions = camp_data["descriptions"]
        descriptions = descriptions.split(',')
        descriptions_to_be_added = []
        for description in descriptions:
            descriptions_to_be_added.append(create_ad_text_asset(google_ads_client, description))

        ad_group_ad.ad.responsive_search_ad.descriptions.extend(descriptions_to_be_added)
        ad_group_ad.ad.responsive_search_ad.path1 = camp_data["path1"]
        ad_group_ad.ad.responsive_search_ad.path2 = camp_data["path2"]

        # Send a request to the server to add a responsive search ad.
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )

        for result in ad_group_ad_response.results:
            print(
                f"Created responsive search ad with resource name "
                f'"{result.resource_name}".'
            )


    except GoogleAdsException as ex:
        handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None



