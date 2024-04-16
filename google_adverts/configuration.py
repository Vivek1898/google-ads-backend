from google.ads.googleads.client import GoogleAdsClient

# credentials = {
#     "developer_token": "6HQT8eShjwwNRQ09ttggzQ",
#     "refresh_token": "1//0gmjkrF5nIj-GCgYIARAAGBASNwF-L9Ira04XA5QOV1tMUGZhQ00roV73y5gOZ83VSuxCMpRFghWNRA74eCyWpuwNfcjKe3OytCs",
#     "client_id": "192111549996-b7oh4f6frrkbd1uls0onjhsf75eilko3.apps.googleusercontent.com",
#     "client_secret": "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",
#     "use_proto_plus": "True",
#     "login_customer_id":"2544551178" #? test manager id
# }

credentials = {
    "developer_token": "dNgift4mNqKNEl-IIwKA4A",
    "refresh_token": "1//0gBWWbBEwL6nMCgYIARAAGBASNwF-L9IrGGvRPAOlhQCjvT7IuW452PIgff9MFxOzHNJKtLUVt_78d7hoFv01IIsmf3Ur1W6jaUs",
    "client_id": "939446384253-4fppn78g2l7lcakcq26qs8kqnr73u4nk.apps.googleusercontent.com",
    "client_secret": "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",
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