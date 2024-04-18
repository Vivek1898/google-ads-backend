from google.ads.googleads.errors import GoogleAdsException
from services.auth_service import verify_auth_token
from services.client_service import google_ads_client as get_google_ads_client
from exception.handle_google_ads_exception import handle_google_ads_exception
from fastapi.responses import JSONResponse


def create_ad_text_asset(google_ads_client, text, pinned_field=None):
    ad_text_asset = google_ads_client.get_type("AdTextAsset")
    ad_text_asset.text = text
    if pinned_field:
        ad_text_asset.pinned_field = pinned_field
    return ad_text_asset


def create_ad_text_asset_with_customizer(google_ads_client, customizer_attribute_name):
    ad_text_asset = google_ads_client.get_type("AdTextAsset")
    ad_text_asset.text = f"{{={customizer_attribute_name}}}"
    return ad_text_asset


def create_customizer_attribute(client, customer_id, customizer_attribute_name):
    """Creates a customizer attribute with the given customizer attribute name.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
        customizer_attribute_name: the name for the customizer attribute.

    Returns:
        A resource name for a customizer attribute.
    """
    # Create a customizer attribute operation for creating a customizer
    # attribute.
    operation = client.get_type("CustomizerAttributeOperation")
    # Create a customizer attribute with the specified name.
    customizer_attribute = operation.create
    customizer_attribute.name = customizer_attribute_name
    # Specify the type to be 'PRICE' so that we can dynamically customize the
    # part of the ad's description that is a price of a product/service we
    # advertise.
    customizer_attribute.type_ = client.enums.CustomizerAttributeTypeEnum.PRICE

    # Issue a mutate request to add the customizer attribute and prints its
    # information.
    customizer_attribute_service = client.get_service(
        "CustomizerAttributeService"
    )
    response = customizer_attribute_service.mutate_customizer_attributes(
        customer_id=customer_id, operations=[operation]
    )
    resource_name = response.results[0].resource_name

    print(f"Added a customizer attribute with resource name: '{resource_name}'")

    return resource_name


def link_customizer_attribute_to_customer(
        client, customer_id, customizer_attribute_resource_name
):
    """Links the customizer attribute to the customer.

    Args:
        client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        customizer_attribute_resource_name: a resource name for  customizer
            attribute.
    """
    # Create a customer customizer operation.
    operation = client.get_type("CustomerCustomizerOperation")
    # Create a customer customizer with the value to be used in the responsive
    # search ad.
    customer_customizer = operation.create
    customer_customizer.customizer_attribute = (
        customizer_attribute_resource_name
    )
    customer_customizer.value.type_ = (
        client.enums.CustomizerAttributeTypeEnum.PRICE
    )
    # The ad customizer will dynamically replace the placeholder with this value
    # when the ad serves.
    customer_customizer.value.string_value = "100USD"

    customer_customizer_service = client.get_service(
        "CustomerCustomizerService"
    )
    # Issue a mutate request to create the customer customizer and prints its
    # information.
    response = customer_customizer_service.mutate_customer_customizers(
        customer_id=customer_id, operations=[operation]
    )
    resource_name = response.results[0].resource_name

    print(
        f"Added a customer customizer to the customer with resource name: '{resource_name}'"
    )


def create_ad(request, ad_data):
    try:
        print("Here to create an ad for given data - ")
        print(request, ad_data)

        user = verify_auth_token(request)
        if not user:
            return {"error": "Please login to access this resource"}

        print(user)

        client = get_google_ads_client(user, ad_data)
        if not client:
                return {"error": "Unable to get Google Ads client"}

        # if ad_data.get("customizer_attribute_name"):
        #     print("Customizer attribute name is present")
        #     customizer_attribute_resource_name = create_customizer_attribute(
        #         client, ad_data.get("customer_id"), ad_data.get("customizer_attribute_name")
        #     )
        #     print(f"Customizer attribute created: {customizer_attribute_resource_name}")
        #     link_customizer_attribute_to_customer(client, ad_data.get("customer_id"),
        #                                           customizer_attribute_resource_name)

        customer_id = ad_data.get("customer_id")
        ad_group_id = ad_data.get("ad_group_id")
        final_urls = ad_data.get("final_urls")
        headlines = ad_data.get("headlines")
        descriptions = ad_data.get("descriptions")
        path1 = ad_data.get("path1")
        path2 = ad_data.get("path2")

        customizer_attribute_name = ad_data.get("customizer_attribute_name")

        ad_group_ad_service = client.get_service("AdGroupAdService")

        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
        ad_group_ad.ad_group = ad_group_ad_service.ad_group_path(
            customer_id, ad_group_id
        )


        # Set final URLs
        ad_group_ad.ad.final_urls.extend(final_urls)

        isPinHeadline = True
        pinned_headline = None
        headlines_to_be_added = []
        for headline in headlines:
            if isPinHeadline:
                served_asset_enum = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
                pinned_headline = create_ad_text_asset(client, headline, served_asset_enum)
                headlines_to_be_added.append(pinned_headline)
                isPinHeadline = False
            else:
                headlines_to_be_added.append(create_ad_text_asset(client, headline))

        ad_group_ad.ad.responsive_search_ad.headlines.extend(headlines_to_be_added)



        # description_2 = None
        #
        # if customizer_attribute_name:
        #     description_2 = create_ad_text_asset_with_customizer(client, customizer_attribute_name)
        # else:
        #     description_2 = create_ad_text_asset(client, "Desc 2 testing")
        descriptions_to_be_added = []
        for description in descriptions:
            descriptions_to_be_added.append(create_ad_text_asset(client, description))
        # if description_2:
        #     descriptions_to_be_added.append(description_2)
        # descriptions.extend([description_2])
        print("=================== descriptions =====================")
        print(descriptions)

        ad_group_ad.ad.responsive_search_ad.descriptions.extend(descriptions_to_be_added)

        # Set paths
        ad_group_ad.ad.responsive_search_ad.path1 = path1
        ad_group_ad.ad.responsive_search_ad.path2 = path2
        print("=================== ad_group_ad =====================")
        # print(ad_group_ad)
        # Send a request to the server to add a responsive search ad
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        print("=================== ad_group_ad_response =====================")
        print(ad_group_ad_response)

        print(f"Created ad: {ad_group_ad_response.results[0].resource_name}")
        return {
            "message": "Ad created successfully",
            "data": {
                "ad": ad_group_ad_response.results[0].resource_name
            }
        }

    except GoogleAdsException as ex:

       return  handle_google_ads_exception(ex)


def list_ads(request, ad_data):
    try:
        user = verify_auth_token(request)
        if not user:
            return {"error": "Please login to access this resource"}

        print(user)
        client = get_google_ads_client(user, ad_data)
        if not client:
            return {"error": "Unable to get Google Ads client"}

        customer_id = ad_data.get("customer_id")
        ad_group_id = ad_data.get("ad_group_id")

        ad_group_ad_service = client.get_service("GoogleAdsService")
        # ga_service = client.get_service("GoogleAdsService")
        query = (
            f"SELECT "
            f"ad_group_ad.action_items, "
            f"ad_group_ad.ad.added_by_google_ads, "
            f"ad_group_ad.ad.app_ad.descriptions, "
            f"ad_group_ad.ad.app_ad.headlines, "
            f"ad_group_ad.ad.name, "
            # f"ad_group_ad.ad.app_ad.html5_media_bundles, "
            f"ad_group_ad.ad.app_pre_registration_ad.descriptions, "
            f"ad_group_ad.ad.app_engagement_ad.videos, "
            f"ad_group_ad.ad.app_engagement_ad.headlines, "
            f"ad_group_ad.status, "
            f"ad_group_ad.resource_name, "
            f"ad_group_ad.policy_summary.review_status, "
            # f"ad_group_ad.policy_summary.policy_topic_entries, "
            f"ad_group_ad.labels, "
            f"ad_group_ad.ad_strength, "
            f"ad_group_ad.ad_group, "
            # f"ad_group_ad.ad.video_responsive_ad.videos, "
            f"ad_group_ad.ad.video_responsive_ad.long_headlines, "
            f"ad_group_ad.ad.video_responsive_ad.headlines, "
            f"ad_group_ad.ad.video_responsive_ad.descriptions, "
            f"ad_group_ad.policy_summary.approval_status, "
            # f"ad_group_ad.ad.video_responsive_ad.companion_banners, "
            # f"ad_group_ad.ad.video_responsive_ad.breadcrumb2, "
            f"ad_group_ad.ad.type, "
            f"ad_group_ad.ad.travel_ad, "
            f"ad_group_ad.ad.shopping_smart_ad, "
            f"ad_group_ad.ad.shopping_product_ad, "
            f"ad_group_ad.ad.name, "
            f"ad_group_ad.ad.resource_name, "
            f"ad_group_ad.ad.id, "
            f"ad_group_ad.ad.final_urls, "
            f"ad_group_ad.ad.expanded_text_ad.description2, "
            f"ad_group_ad.ad.expanded_text_ad.headline_part1, "
            f"ad_group_ad.ad.expanded_text_ad.description, "
            f"ad_group_ad.ad.expanded_text_ad.headline_part2, "
            f"ad_group_ad.ad.expanded_dynamic_search_ad.description2, "
            f"ad_group_ad.ad.expanded_dynamic_search_ad.description, "
            f"ad_group_ad.ad.display_url, "
            f"ad_group_ad.ad.call_ad.headline1, "
            f"ad_group_ad.ad.call_ad.headline2, "
            f"metrics.conversions, "
            f"metrics.conversions_value, "
            f"metrics.absolute_top_impression_percentage, "
            f"metrics.active_view_cpm, "
            f"metrics.active_view_ctr, "
            f"metrics.active_view_impressions, "
            f"metrics.active_view_measurability, "
            f"metrics.active_view_measurable_cost_micros, "
            f"metrics.active_view_measurable_impressions, "
            f"metrics.active_view_viewability, "
            f"metrics.all_conversions, "
            f"metrics.all_conversions_by_conversion_date, "
            f"metrics.all_conversions_from_interactions_rate, "
            f"metrics.all_conversions_value, "
            f"metrics.all_conversions_value_by_conversion_date, "
            f"metrics.all_new_customer_lifetime_value, "
            f"metrics.average_cost, "
            f"metrics.clicks, "
            f"metrics.bounce_rate, "
            f"metrics.average_time_on_site, "
            f"metrics.average_page_views, "
            f"metrics.average_cpv, "
            f"metrics.average_cpm, "
            f"metrics.average_cpe, "
            f"metrics.average_cpc, "
            f"metrics.conversions_by_conversion_date, "
            f"metrics.conversions_from_interactions_rate, "
            f"metrics.ctr, "
            f"metrics.cost_micros, "
            f"metrics.cost_per_all_conversions, "
            f"metrics.cost_per_conversion, "
            f"metrics.cost_per_current_model_attributed_conversion, "
            f"metrics.cross_device_conversions, "
            f"metrics.conversions_value_by_conversion_date, "
            f"metrics.current_model_attributed_conversions, "
            f"metrics.engagement_rate, "
            f"metrics.current_model_attributed_conversions_value, "
            f"metrics.interactions, "
            f"metrics.interaction_rate, "
            f"metrics.impressions, "
            f"metrics.gmail_saves, "
            f"metrics.gmail_forwards, "
            f"metrics.engagements, "
            f"metrics.value_per_conversions_by_conversion_date, "
            f"metrics.value_per_current_model_attributed_conversion, "
            f"metrics.video_quartile_p25_rate, "
            f"metrics.video_views, "
            f"metrics.video_view_rate, "
            f"metrics.view_through_conversions "
            f"FROM ad_group_ad "
            f"WHERE ad_group.id = {ad_group_id}"
        )

        response = ad_group_ad_service.search(customer_id=customer_id, query=query)

        result = []
        for row in response:
            result.append({
                "id": row.ad_group_ad.ad.id,
                "name": row.ad_group_ad.ad.name,
                "ctr": row.metrics.ctr,
                "cost_micros": row.metrics.cost_micros,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
                "average_cpc": row.metrics.average_cpc,
                "conversions_value": row.metrics.conversions_value,
                "absolute_top_impression_percentage": row.metrics.absolute_top_impression_percentage,
                "active_view_cpm": row.metrics.active_view_cpm,
                "active_view_ctr": row.metrics.active_view_ctr,
                "active_view_impressions": row.metrics.active_view_impressions,
                "active_view_measurability": row.metrics.active_view_measurability,
                "cost_per_conversion": row.metrics.cost_per_conversion,
                "engagement_rate": row.metrics.engagement_rate,
                "interactions": row.metrics.interactions,
                "impressions": row.metrics.impressions,
                "resource_name": row.ad_group_ad.resource_name,
                "status": row.ad_group_ad.status,
            })
            print(result)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Ad list fetched successfully",
                "ad_details": result,
            }
        )
    except GoogleAdsException as ex:
        return handle_google_ads_exception(ex)





