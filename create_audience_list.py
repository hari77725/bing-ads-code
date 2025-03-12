# Description: This script creates a new audience list in Bing Ads. (Deprecated)
from bingads.service_client import ServiceClient
from bingads.authorization import *
from bingads.v13.bulk import *
# from bingads.v13.bulk.entities.audiences import CustomAudience
from main import set_elements_to_none
import traceback

DEVELOPER_TOKEN = 'BBD37VB98'
ACCOUNT_ID = '526065840'
CUSTOMER_ID = '355788527'
CLIENT_ID='4c0b021c-00c3-4508-838f-d3127e8167ff'
CLIENT_STATE='ClientStateGoesHere'

def log_soap_fault(error):
    """Helper to log SOAP fault details"""
    if hasattr(error, 'FaultDetail'):
        print(f"FaultDetail: {error.FaultDetail}")
    if hasattr(error, 'TrackingId'):
        print(f"TrackingId: {error.TrackingId}")
    print(f"Stack Trace: {traceback.format_exc()}")

def get_campaign_management_service()-> ServiceClient:
    """
    Get the campaign management service client.
    
    Returns:
        CampaignManagementService: An instance of the campaign management service client
    """

    authorization_data = AuthorizationData(
            account_id=ACCOUNT_ID,
            customer_id=CUSTOMER_ID,
            developer_token=DEVELOPER_TOKEN,
            authentication=OAuthDesktopMobileAuthCodeGrant(
                client_id=CLIENT_ID,
                env='sandbox',
            )
    )

    authorization_data.authentication.request_oauth_tokens_by_refresh_token('M.C1_EUS.0.U.-BOVDZJsLDmzsX0cC!6guYba80l55Sc!H8lesZ4!OfWnxsiMcZvsBuvr20nwukWfpembegBbI2KPR5vTDcd8hcpgH5fWy9kB06RmYG0GMw0EQf8Mn!toyu0IQYhmbeEFFMwG2fdqW9nWU62b63CSCNevWhZu5d!pa5PN0FbGzvyMHutPUiaUvqOb8os4V8AkGfmo739yKt3*ze*O331n5ugbVQSZ0Xzv*hcNi1hsoDtgxSVVc3gW5!BhdxpcbZdaRCdz5XSR4FIvDtyXbjJHSYpCKCz3XbRwv5VGhMhIh*YmA7koQ*VWGaLV35w5avQfGVCwk4uilQ3SxnkiTQQapk2aL4DRBXj47ZtP78CQEdW12BnMQyaxA*bcqx8lNR5HoJOj!zuxwmDDOp0E4vivGa5H5CPwGal3QoSVN7mat7JEyOTDNKu4B8!j23KHIkpxn!w$$')
    
    campaign_service = ServiceClient(
        service='CampaignManagementService',
        version=13,
        authorization_data=authorization_data,
        environment='sandbox'
    )
    
    return campaign_service


def add_audience_list()->None:

    campaign_service = get_campaign_management_service()
    # customer_list = set_elements_to_none(campaign_service.factory.create('CustomerList'))
    # customer_list.AudienceNetworkSize = 300
    # customer_list.Description = "Created from create Audience list sdk"
    # customer_list.Id = None
    # customer_list.MembershipDuration = 30
    # customer_list.Name = "Test Audience List from campaign sdk"
    # customer_list.ParentId = ACCOUNT_ID
    # customer_list.Scope = "Customer"
    # customer_list.SearchSize = 300
    # customer_list.SupportedCampaignTypes = campaign_service.factory.create('ns3:ArrayOfstring').string.append("Audience")
    # customer_list.Type = "CustomerList"

    campaign_types = campaign_service.factory.create('ns3:ArrayOfstring')
    campaign_types.string = ['Audience']  # Direct assignment instead of append
    
    # Create customer list
    customer_list = campaign_service.factory.create('Audience')
    customer_list = set_elements_to_none
    customer_list.AudienceNetworkSize = 300
    customer_list.Description = "Created from create Audience list sdk"
    customer_list.Id = None
    customer_list.MembershipDuration = 30
    customer_list.Name = "Test Audience List from campaign sdk"
    customer_list.ParentId = ACCOUNT_ID
    customer_list.Scope = "Customer"
    customer_list.SearchSize = 300
    customer_list.SupportedCampaignTypes = campaign_types
    customer_list.Type = "CustomerList"

    # Create array of audiences
    # audiences = campaign_service.factory.create('ArrayOfAudience')
    # audiences.Audience = [customer_list]


    try:
        campaign_service.AddAudiences(
            Audiences=customer_list
        )
    except Exception as e:
        print("Error adding audience list: ")



    


def add_audience_data()->None:

    authorization_data = AuthorizationData(
        account_id='526065840',
        customer_id='355788527',
        developer_token='BBD37VB98',
        authentication=None
   )
    
    



if __name__ == "__main__":
    add_audience_list()