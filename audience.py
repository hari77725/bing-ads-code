from main import main


from bingads.service_client import ServiceClient
from bingads.v13.bulk import *
from bingads.v13 import *
from bingads.authorization import *

class BingAdsAudienceUploader:
    def __init__(self, client_id, client_secret, developer_token, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret 
        self.developer_token = developer_token
        self.refresh_token = refresh_token

    def authenticate(self, account_id, customer_id):
        authentication = OAuthWebAuthCodeGrant(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token
        )

        self.authorization_data = AuthorizationData(
            account_id=account_id,
            customer_id=customer_id,
            developer_token=self.developer_token,
            authentication=authentication
        )

    def upload_audience(self, audience_name, description, membership_duration=30):
        try:
            audience_service = ServiceClient(
                'AudienceManagementService', 
                version=13,
                authorization_data=self.authorization_data,
                environment='production'
            )

            audience = {
                'Name': audience_name,
                'Description': description,
                'MembershipDuration': membership_duration,
                'Scope': 'Account',
                'Type': 'RemarketingList',
                'CustomerShare': {
                    'CustomerAccountShares': None,
                    'CustomerIds': None
                }
            }

            response = audience_service.AddAudiences(Audiences=[audience])
            return response.AudienceIds[0] if response else None

        except Exception as e:
            print(f"Error uploading audience: {str(e)}")
            return None

# Usage example:
if __name__ == "__main__":
    uploader = BingAdsAudienceUploader(
        client_id="your_client_id",
        client_secret="your_client_secret", 
        developer_token="your_developer_token",
        refresh_token="your_refresh_token"
    )

    uploader.authenticate(
        account_id="your_account_id",
        customer_id="your_customer_id"
    )

    audience_id = uploader.upload_audience(
        audience_name="Test Audience",
        description="Test audience description",
        membership_duration=30
    )

    print(f"Uploaded audience ID: {audience_id}")