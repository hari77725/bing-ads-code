from datetime import datetime, timedelta, timezone
from bingads.authorization import *
from campaignmanagement_example_helper import *

from main import *

# Required
# DEVELOPER_TOKEN='BBD37VB98' # Universal token for sandbox
DEVELOPER_TOKEN='1455DHRGAV939488'
ENVIRONMENT='production' # If you use 'production' then you must also update the DEVELOPER_TOKEN value.

# The CLIENT_ID is required and CLIENT_STATE is recommended.
# The REFRESH_TOKEN should always be in a secure location.
CLIENT_ID='4c0b021c-00c3-4508-838f-d3127e8167ff'
CLIENT_STATE='ClientStateGoesHere'
REFRESH_TOKEN="refresh.txt"


def main(campaign_service,authorization_data):
    # import logging
    # logging.basicConfig(level=logging.INFO)
    # logging.getLogger('suds.client').setLevel(logging.DEBUG)
    # logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)

    try:
        # offline_conversion_goal_name = "My Offline Conversion Goal"

        # conversion_goals=campaign_service.factory.create('ArrayOfConversionGoal')

        # offline_conversion_goal=set_elements_to_none(campaign_service.factory.create('OfflineConversionGoal'))
        # offline_conversion_goal.GoalCategory = "Purchase"
        # # Determines how long after a click that you want to count offline conversions. 
        # offline_conversion_goal.ConversionWindowInMinutes = 43200
        # # If the count type is 'Unique' then only the first offline conversion will be counted.
        # # By setting the count type to 'All', then all offline conversions for the same
        # # MicrosoftClickId with different conversion times will be added cumulatively. 
        # offline_conversion_goal.CountType = 'All'
        # offline_conversion_goal.Name = offline_conversion_goal_name
        # # The default conversion currency code and value. Each offline conversion can override it.
        # offline_conversion_goal_revenue=set_elements_to_none(campaign_service.factory.create('ConversionGoalRevenue'))
        # offline_conversion_goal_revenue.CurrencyCode=None
        # offline_conversion_goal_revenue.Type='FixedValue'
        # offline_conversion_goal_revenue.Value=5.00
        # offline_conversion_goal.Revenue = offline_conversion_goal_revenue
        # offline_conversion_goal.Scope = 'Account'
        # offline_conversion_goal.Status = 'Active'
        # # The TagId is inherited from the ConversionGoal base class,
        # # however, Offline Conversion goals do not use a UET tag.
        # offline_conversion_goal.TagId = None
        # conversion_goals.ConversionGoal.append(offline_conversion_goal)

        # output_status_message("-----\nAddConversionGoals:")
        # add_conversion_goals_response=campaign_service.AddConversionGoals(
        #     ConversionGoals=conversion_goals)
        # output_status_message("ConversionGoalIds:")
        # output_array_of_long(add_conversion_goals_response.ConversionGoalIds)
        # output_status_message("PartialErrors:")
        # output_array_of_batcherror(add_conversion_goals_response.PartialErrors)
        
        # # Find the conversion goals that were added successfully. 

        # conversion_goal_ids = []
        # for goal_id in add_conversion_goals_response.ConversionGoalIds['long']:
        #     if goal_id is not None:
        #         conversion_goal_ids.append(goal_id)
        
        # conversion_goal_types='OfflineConversion'
        
        # return_additional_fields = 'ViewThroughConversionWindowInMinutes'
        
        # output_status_message("-----\nGetConversionGoalsByIds:")
        # get_conversion_goals_by_ids_response = campaign_service.GetConversionGoalsByIds(
        #     ConversionGoalIds={'long': conversion_goal_ids}, 
        #     ConversionGoalTypes=conversion_goal_types,
        #     ReturnAdditionalFields=return_additional_fields
        # )
        # output_status_message("ConversionGoals:")
        # output_array_of_conversiongoal(get_conversion_goals_by_ids_response.ConversionGoals)
        # output_status_message("PartialErrors:")
        # output_array_of_batcherror(get_conversion_goals_by_ids_response.PartialErrors)

        offline_conversions=campaign_service.factory.create('ArrayOfOfflineConversion')

        offline_conversion=set_elements_to_none(campaign_service.factory.create('OfflineConversion'))
        # If you do not specify an offline conversion currency code, 
        # then the 'CurrencyCode' element of the goal's 'ConversionGoalRevenue' is used.
        offline_conversion.ConversionCurrencyCode = "USD"
        # The conversion name must match the 'Name' of the 'OfflineConversionGoal'.
        # If it does not match you won't observe any error, although the offline
        # conversion will not be counted.
        offline_conversion.ConversionName = 'test_offline'
        # The date and time must be in UTC, should align to the date and time of the 
        # recorded click (MicrosoftClickId), and cannot be in the future.
        offline_conversion.ConversionTime = datetime.now(timezone.utc) - timedelta(hours=1)
        # If you do not specify an offline conversion value, 
        # then the 'Value' element of the goal's 'ConversionGoalRevenue' is used.
        offline_conversion.ConversionValue = 120.00
        offline_conversion.HashedEmailAddress = "7105b50422b6490672243b377bfaa352dc2ebcd7ad8fb80b11f4f8adb9f7537e"
        offline_conversion.HashedPhoneNumber = "910a625c4ba147b544e6bd2f267e130ae14c591b6ba9c25cb8573322dedbebd0"
        offline_conversions.OfflineConversion.append(offline_conversion)

        # After the OfflineConversionGoal is set up, wait two hours before sending Bing Ads the offline conversions. 
        # This example would not succeed in production because we created the goal very recently i.e., 
        # please see above call to AddConversionGoals. 

        output_status_message("-----\nApplyOfflineConversions:")
        apply_offline_conversions_response = campaign_service.ApplyOfflineConversions(
            OfflineConversions=offline_conversions)
        output_status_message("PartialErrors:")
        output_array_of_batcherror(apply_offline_conversions_response)

    except WebFault as ex:
        print("WebFault: {0}".format(ex.fault))
        output_webfault_errors(ex)
    except Exception as ex:
        print("Exception: {0}".format(ex))
        output_status_message(ex)



if __name__ == '__main__':
    print("Loading the web service client proxies...")
    
    authorization_data=AuthorizationData(
        account_id='187005313',
        customer_id='254303037',
        developer_token=DEVELOPER_TOKEN,
        authentication=None,
    )
    

    campaign_service=ServiceClient(
        service='CampaignManagementService', 
        version=13,
        authorization_data=authorization_data, 
        environment=ENVIRONMENT,
    )
    authenticate(authorization_data)

    main(campaign_service,authorization_data)
        
    