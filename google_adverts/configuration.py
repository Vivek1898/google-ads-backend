from google.ads.googleads.client import GoogleAdsClient
import os
from dotenv import load_dotenv
load_dotenv()


credentials = {
    "developer_token": os.getenv("DEVELOPER_TOKEN"),
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "use_proto_plus": "True",
    "login_customer_id":"5503786086" #? test manager id
}

# credentials = {
#     "developer_token": "",
#     "refresh_token": "",
#     "client_id": "",
#     "client_secret": "",
#     "use_proto_plus": "",
#     "login_customer_id":"" #? manager id
# }


class GoogleAds:
    google_ads_client = None

    def __init__(self):
        if GoogleAds.google_ads_client is None:
            GoogleAds.google_ads_client = GoogleAdsClient.load_from_dict(credentials)

    def get_google_ads_client(self):
        return GoogleAds.google_ads_client


if __name__ == "__main__":
    google_ads_client_instance = GoogleAds()
    print(google_ads_client_instance.get_google_ads_client())
    google_ads_client_instance_two = GoogleAds()
    print(google_ads_client_instance_two.get_google_ads_client())
    #     # ! why two different instances created here