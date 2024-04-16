from google_adverts.configuration import GoogleAds
from exception.handle_google_ads_exception import handle_google_ads_exception
from google.ads.googleads.errors import GoogleAdsException

def add_keywords_in_ad_group(google_ads_client, camp_data):
    try:
        print(google_ads_client, camp_data)
        ad_group_service = google_ads_client.get_service("AdGroupService")
        ad_group_criterion_service = google_ads_client.get_service("AdGroupCriterionService")
        customer_id = str(camp_data["customer_id"])
        ad_group_id = str(camp_data["ad_group_id"])
        keywords = camp_data["keywords"]
        keywords = keywords.split(',')

        keyword_operations = []

        for keyword in keywords:
            print(keyword)
            # Create keyword.
            ad_group_criterion_operation = google_ads_client.get_type("AdGroupCriterionOperation")
            ad_group_criterion = ad_group_criterion_operation.create

            ad_group_criterion.ad_group = ad_group_service.ad_group_path(
                customer_id, ad_group_id
            )
            ad_group_criterion.status = google_ads_client.enums.AdGroupCriterionStatusEnum.ENABLED
            ad_group_criterion.keyword.text = keyword
            ad_group_criterion.keyword.match_type = (
                google_ads_client.enums.KeywordMatchTypeEnum.PHRASE
            )

            keyword_operations.append(ad_group_criterion_operation)

        # Optional field
        # All fields can be referenced from the protos directly.
        # The protos are located in subdirectories under:
        # https://github.com/googleapis/googleapis/tree/master/google/ads/googleads
        # ad_group_criterion.negative = True

        # Optional repeated field
        # ad_group_criterion.final_urls.append('https://www.example.com')

        # Add keywords
        ad_group_criterion_response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=keyword_operations,
        )

        print(
            "Created keyword "
            f"{ad_group_criterion_response.results[0].resource_name}."
        )


    except GoogleAdsException as ex:
        handle_google_ads_exception(ex)
    except Exception as err:
        print(f"Caught an exception while creating a  campaign for {camp_data} - {err}")
        return None



