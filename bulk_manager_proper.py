from datetime import datetime
import sys
from bingads.authorization import AuthorizationData, OAuthDesktopMobileAuthCodeGrant , OAuthWebAuthCodeGrant
from bingads.v13.bulk import (
    BulkServiceManager, 
    SubmitDownloadParameters, 
    BulkFileReader, 
    BulkFileWriter, 
    BulkCustomerList, 
    ResultFileType, 
    FileUploadParameters,
    BulkCustomerListItem,
    DownloadParameters
)

from bingads.service_client import ServiceClient
from typing import List, Generator, Optional , Any
import logging
import os
import csv
csv.field_size_limit(sys.maxsize)
from campaignmanagement_example_helper import output_array_of_batcherror, output_status_message
from main import set_elements_to_none
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEVELOPER_TOKEN = 'BBD37VB98'
ACCOUNT_ID = '526065840'
CUSTOMER_ID = '355788527'
CLIENT_ID = 'CID'
CLIENT_SECRET = 'CLS'
REFRESH_TOKEN = 'M.C556_BL2.0.U.-Ch2T0kZMPftk*MCmWB4iUNkrVe46jLJ1ge7x4C4rBsEsmfhCYA7eHvBLf35uDtwvE96IJ!adWFKyvZ5z*s1YFKgPWv6jnlyAPSvWm57hjBr1EpyB1wZo2ioHlLJzs366m7uTigeaChlzDcJiklXo3aRxvPG6dZAPI38d!IJ9ZTHATDJZ6d!wbTfz4fq9gLS2YfSu4s92Tlrr1IRIRccnfUXf3nR2LQmrzPAla2lsXrgd9iUfHZudq5D1OS7lJQY33aARp4MH01q6hjLT66EjD3Qe7NHjMMDe8udpksluLhCx76poUkdsFbxO1osi7S*JX4DKvD9hQmKUgu2vyVxXnEX3C!arjcXGwot54JOb9tKyx14Y7ofGwY7Y3is33AYRk*4rwtvpPoIEK8nBqt3MYsqTUpr4C7S!6TrnUHwxZ2f8'

class BingAdsManager:
    def __init__(self):
        self.authorization_data = self._get_authorization_data()
        self.bulk_service_manager = self._get_bulk_service_manager()
        self.campaign_service = self._get_campaign_service()

    def _get_authorization_data(self) -> AuthorizationData:
        auth = AuthorizationData(
            account_id=ACCOUNT_ID,
            customer_id=CUSTOMER_ID,
            developer_token=DEVELOPER_TOKEN,
            authentication=OAuthWebAuthCodeGrant(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                env='production'
            )
        )
        auth.authentication.request_oauth_tokens_by_refresh_token(REFRESH_TOKEN)
        return auth

    def _get_bulk_service_manager(self) -> BulkServiceManager:
        return BulkServiceManager(
            authorization_data=self.authorization_data,
            poll_interval_in_milliseconds=35000,
            environment='sandbox'
        )
    
    def _get_all_customer_lists(self) -> List[BulkCustomerList]:
        bulk_service_manager = self._get_bulk_service_manager()
        submit_download_parameters = SubmitDownloadParameters(
            data_scope=['EntityData'],
            download_entities=['CustomerLists'],
            file_type='Csv'
        )
        bulk_file_operation = bulk_service_manager.submit_download(submit_download_parameters)
        download_status = bulk_file_operation.track(timeout_in_milliseconds=3600000)
        if not bulk_file_operation:
            raise Exception("Failed to submit download operation")
        
        if download_status.status != 'Completed':
            raise Exception(f"Download failed with status: {download_status.status}")
    
        result_file_path = bulk_file_operation.download_result_file(
            result_file_directory='./',
            result_file_name='result_latest.csv',
            decompress=True,
            overwrite=True,
            timeout_in_milliseconds=3600000
        )
        
        print(f"Download result file: {result_file_path}")

    def _get_campaign_service(self) -> ServiceClient:
        return ServiceClient(
            service='CampaignManagementService',
            version=13,
            authorization_data=self.authorization_data,
            environment='sandbox'
        )
    
    def _get_customer_list_service(self) -> ServiceClient:
        return ServiceClient(
            service='CustomerManagementService',
            version=13,
            authorization_data=self.authorization_data,
            environment='sandbox'
        )

    def getUetTags(self):
        res = self.campaign_service.GetUetTagsByIds()
        print(res)

    def get_all_customer_lists(self) -> List[BulkCustomerList]:
        return self._get_all_customer_lists()

    def create_customer_list(self, name: str, description: str) -> BulkCustomerList:
        campaign_types = self.campaign_service.factory.create('ns3:ArrayOfstring')
        campaign_types.string = ['Audience']

        customer_list = self.campaign_service.factory.create('CustomerList')
        customer_list.AudienceNetworkSize = 30
        customer_list.Description = description
        customer_list.MembershipDuration = 30
        customer_list.Name = name
        customer_list.ParentId = int(ACCOUNT_ID)
        customer_list.Scope = "Customer"
        customer_list.SearchSize = 300
        customer_list.SupportedCampaignTypes = campaign_types
        customer_list.Type = "CustomerList"

        bulk_customer_list = BulkCustomerList()
        bulk_customer_list.customer_list = customer_list
        return bulk_customer_list

    def get_all_audiences_sdk(self):
        res = self.campaign_service.GetAudiencesByIds(None,Type="CustomerList")
        print(res)

    def get_an_audience_sdk(self, audience_id: int | None):
        response=self.campaign_service.GetAudiencesByIds(
                AudienceIds={"long": [audience_id]},
                Type="CustomerList",
        )
        print(response)

    def upload_customer_lists(self, customer_lists: List[BulkCustomerList]) -> None:
        try:
            writer = BulkFileWriter('./upload.csv')
            for entity in customer_lists:
                writer.write_entity(entity)
            writer.close()

            upload_params = FileUploadParameters(
                result_file_directory='./',
                compress_upload_file=True,
                result_file_name='result.csv',
                overwrite_result_file=True,
                upload_file_path='./upload.csv',
                response_mode='ErrorsAndResults'
            )

            bulk_file_path = self.bulk_service_manager.upload_file(
                file_upload_parameters=upload_params,
                progress=lambda x: logger.info(f"Upload progress: {x.percent_complete}%")
            )

            self._process_upload_results(bulk_file_path)

        except Exception as e:
            logger.error(f"Error uploading customer lists: {str(e)}")
            raise

    def update_customer_lists(self, update_id : int , **update_fields: dict[str,Any]) -> None:
        campaign_types = self.campaign_service.factory.create('ns3:ArrayOfstring')
        campaign_types.string = ['Audience']

        customer_list = self.campaign_service.factory.create('CustomerList')
        customer_list.Id = update_id
        
        if 'audience_network_size' in update_fields:
            customer_list.AudienceNetworkSize = update_fields['audience_network_size']
        if 'audience_network_size' not in update_fields:
            customer_list.AudienceNetworkSize = 30
            
        if 'description' in update_fields:
            customer_list.Description = update_fields['description']
            
        if 'membership_duration' in update_fields:
            customer_list.MembershipDuration = update_fields['membership_duration']
        if 'membership_duration' not in update_fields:
            customer_list.MembershipDuration = 30
            
        if 'name' in update_fields:
            customer_list.Name = update_fields['name']
            
        if True:
            customer_list.ParentId = int(ACCOUNT_ID)
        if True:
            customer_list.Scope = "Customer"
        
        if 'search_size' in update_fields:
            customer_list.SearchSize = update_fields['search_size']
        if 'search_size' not in update_fields:
            customer_list.SearchSize = 300
            
        if True:
            customer_list.SupportedCampaignTypes = campaign_types
        if True:
            customer_list.Type = "CustomerList"

        bulk_customer_list = BulkCustomerList()
        bulk_customer_list.customer_list = customer_list

        try:
            self.upload_customer_lists([bulk_customer_list])
        except Exception as e:
            logger.error(f"Error updating customer list: {str(e)}")
            raise

    # def update_audience_data(self, parent_id: int , name : str ):
    #     raise NotImplementedError("Not implemented")
    
    def update_audience_data(self, parent_id: int, name: str, action_type: str = "Add", audience_data: List[str] = None):
        """
        Updates audience data for a customer list with email addresses.
        
        Args:
            parent_id: The ID of the customer list to update
            name: The name of the customer list
            action_type: The action type ("Add", "Remove", or "Replace")
            audience_data: List of email addresses to update
        """
        if not audience_data:
            raise ValueError("audience_data cannot be empty")
        
        if not parent_id and not name:
            raise ValueError("parent_id or name are required")
        
        
        # try:
        #     with BulkFileWriter('./audience_upload.csv') as writer:
        #         campaign_types = self.campaign_service.factory.create('ns3:ArrayOfstring')
        #         campaign_types.string = ['Audience']

        #         for email in audience_data:
        #             bulk_customer_list_item = BulkCustomerListItem()
        #             bulk_customer_list_item.parent_id = parent_id
        #             bulk_customer_list_item.sub_type = "Email"
        #             bulk_customer_list_item.text = email

        #             writer.write_entity(bulk_customer_list_item)

        #         upload_params = FileUploadParameters(
        #             result_file_directory='./',
        #             result_file_name='audience_result.csv',
        #             upload_file_path='./audience_upload.csv',
        #             response_mode='ErrorsAndResults',
        #             compress_upload_file=True,
        #             overwrite_result_file=True,
        #             rename_upload_file_to_match_request_id=False
        #         )

        #         bulk_file_path = self.bulk_service_manager.upload_file(
        #             file_upload_parameters=upload_params,
        #             progress=lambda x: logger.info(f"Upload progress: {x.percent_complete}%")
        #         )

        #         self._process_upload_results(bulk_file_path)


        # except Exception as e:
        #     logger.error(f"Error updating audience data: {str(e)}")
        #     raise

        try:
            # download_parameters=DownloadParameters(
            #     download_entities=['CustomerLists'],
            #     result_file_directory='./',
            #     data_scope=['EntityData'],
            #     result_file_name="existing_lists.csv",
            #     overwrite_result_file=True,
            #     last_sync_time_in_utc=None
            # )

            # self.bulk_service_manager.download_file(download_parameters)

            # for entity in self.read_download_file("".join([os.getcwd(), "/existing_lists.csv"])):
            #     if isinstance(entity, BulkCustomerList):
            #         print(f"Customer List Name: {entity.customer_list.Name}, ID: {entity.customer_list.Id}")
            #     else:
            #         print(entity.__dict__)

            # Create bulk upload file with parent and items
            with BulkFileWriter('./customer_list_upload.csv') as writer:
                # Write parent CustomerList first
                bulk_customer_list = BulkCustomerList()

                customer_list = set_elements_to_none(self.campaign_service.factory.create('CustomerList'))
                print(customer_list)
                customer_list.Id = parent_id
                
                
                bulk_customer_list.customer_list = customer_list
                bulk_customer_list.status = "Active"
                bulk_customer_list.action_type = action_type
                
                entities_to_write = [bulk_customer_list]
                
                # Write CustomerListItems
                for email in audience_data:
                    list_item = BulkCustomerListItem()
                    list_item.parent_id = parent_id
                    list_item.sub_type = "Email"
                    list_item.text = email
                    entities_to_write.append(list_item)

                for entity in entities_to_write:
                    writer.write_entity(entity)

            # Upload combined file
            upload_params = FileUploadParameters(
                result_file_directory='./',
                result_file_name='upload_results.csv',
                upload_file_path='./customer_list_upload.csv',
                response_mode='ErrorsAndResults',
                compress_upload_file=True,
                overwrite_result_file=True
            )
            bulk_file_path = self.bulk_service_manager.upload_file(
            file_upload_parameters=upload_params,
            progress=lambda x: logger.info(f"Upload progress: {x.percent_complete}%")
            )

            return self._process_upload_results(bulk_file_path)

            
        except Exception as e:
            logger.error(f"Error updating audience data: {str(e)}")
            raise

    def search_accounts_by_user_id(self, user_id: int) -> dict:
        """
        Searches for accounts accessible by the given user ID.
    
        Args:
            user_id: The ID of the user.
    
        Returns:
            A dictionary containing account details.
        """
        try:
            # Use CustomerManagementService instead of CampaignManagementService
            customer_service = self._get_customer_list_service()
    
            # Create a request to search accounts by user ID
            search_accounts_request = customer_service.factory.create('SearchAccountsRequest')
            search_accounts_request.UserId = user_id
    
            # Call the service to get accounts
            response = customer_service.SearchAccounts(search_accounts_request)
    
            # Return the accounts from the response
            return response.Accounts
        except Exception as e:
            logger.error(f"Error searching accounts by user ID: {str(e)}")
            raise


    def get_user_data(self):
        """
        Retrieves account details and customer pilot features.
        """
        try:
            # Get the CustomerManagementService client
            customer_service = self._get_customer_list_service()  # Add parentheses here
    
            # Get user details
            get_user_response = customer_service.GetUser(UserId=None)
            user = get_user_response.User
            customer_roles = get_user_response.CustomerRoles
            print("User:")
            print(user)
            
    
        except Exception as e:
            logger.error(f"Error retrieving account data: {str(e)}")
            raise

    def get_accounts_data(self):
        """
        Retrieves account details and customer pilot features.
        """
        try:
            # Get the CustomerManagementService client
            customer_service = self._get_customer_list_service()
            
            # Get accounts info
            get_accounts_response = customer_service.GetAccountsInfo()
            
            # Loop through the accounts and log details
            if hasattr(get_accounts_response, 'AccountInfo') and get_accounts_response.AccountInfo:
                for account in get_accounts_response.AccountInfo:
                    logger.info(
                        f"Account ID: {account.Id}, "
                        f"Name: {account.Name}, "
                        f"Number: {account.Number}, "
                        f"Status: {account.AccountLifeCycleStatus}, "
                        f"Pause Reason: {account.PauseReason}"
                    )
            else:
                logger.info("No accounts found.")
        except Exception as e:
            logger.error(f"Error retrieving account data: {str(e)}")
            raise

    

    def update_audience_data_method(self, parent_id: int, name: str, action_type: str = "Add", audience_data: List[str] = None):
        try:
            # customer_list = set_elements_to_none(self.campaign_service.factory.create('CustomerList'))
            # customer_list.Id = parent_id

            # print(customer_list)

            customer_list_item = set_elements_to_none(self.campaign_service.factory.create('CustomerListUserData'))
            print(customer_list_item)

            customer_list_item.ActionType = action_type
            customer_list_item.AudienceId = parent_id
            customer_list_item.CustomerListItemSubType = "Email"

            arr = self.campaign_service.factory.create('ns3:ArrayOfstring')
            
            for email in audience_data:
                arr.string.append(email)

            customer_list_item.CustomerListItems = arr

            response = self.campaign_service.ApplyCustomerListUserData(customer_list_item)
            output_status_message("PartialErrors:")
            output_array_of_batcherror(response)
        except Exception as e:
            logger.error(f"Error updating audience data: {str(e)}")
            raise




    def _process_upload_results(self, bulk_file_path: str) -> None:
        try:
            entities = self._read_bulk_file(bulk_file_path)
            for entity in entities:
                if isinstance(entity, BulkCustomerList):
                    logger.info(f"Uploaded customer list: {entity.customer_list.Name}")
                if isinstance(entity, BulkCustomerListItem) and entity._errors:
                    for error in entity._errors:
                        logger.error(
                            f"\nBulk Upload Error:"
                            f"\n  Error Code: {error.error}"
                            f"\n  Error Number: {error.number}"
                            f"\n  Item Text: {entity.text}"
                            f"\n  Parent ID: {entity.parent_id}"
                            f"\n  Sub Type: {entity.sub_type}"
                            f"\n  Editorial Reason Code: {getattr(error, 'editorial_reason_code', 'N/A')}"
                            f"\n  Editorial Location: {getattr(error, 'editorial_location', 'N/A')}"
                            f"\n  Editorial Term: {getattr(error, 'editorial_term', 'N/A')}"
                        )

                if(isinstance, BulkCustomerList):
                    logger.info(
                        f"\nSuccessful Upload:"
                        f"\n{entity}"
                        
                    )
                else:
                    logger.info(
                        f"\nSuccessful Upload:"
                        f"\n  Text: {entity.text}"
                        f"\n  Parent ID: {entity.parent_id}"
                        f"\n  Sub Type: {entity.sub_type}"
                    )
        except Exception as e:
            logger.error(f"Error processing upload results: {str(e)}")
            raise

    def _read_bulk_file(self, file_path: str) -> Generator:
        with BulkFileReader(
            file_path=file_path,
            result_file_type=ResultFileType.upload,
            file_type='Csv'
        ) as reader:
            for entity in reader:
                yield entity


    def read_download_file(self, file_path: str) -> Generator:
        with BulkFileReader(
            file_path=file_path,
            result_file_type=ResultFileType.full_download,
            file_type='Csv'
        ) as reader:
            for entity in reader:
                yield entity

    def create_audience_sdk(self):
        campaign_types = self.campaign_service.factory.create('ns3:ArrayOfstring')
        campaign_types.string = ['Audience']

        customer_list = self.campaign_service.factory.create('CustomerList')
        customer_list.AudienceNetworkSize = 30
        customer_list.Description = "Created from SDK"
        customer_list.MembershipDuration = 30
        customer_list.Name = "SDK Customer List 2"
        customer_list.Scope = "Customer"
        customer_list.SearchSize = 300
        customer_list.SupportedCampaignTypes = campaign_types
        customer_list.Type = "CustomerList"


        try:
            audiences = set_elements_to_none(self.campaign_service.factory.create('ArrayOfAudience'))
            audiences.Audience = customer_list
            response = self.campaign_service.AddAudiences(
                Audiences=[audiences]
            )

            if hasattr(response, 'PartialErrors') and response.PartialErrors:
                logger.error("Partial Errors:")
                for error in response.PartialErrors.BatchError:
                    logger.error(f"Error Code: {error.Code}")
                    logger.error(f"Message: {error.Message}")
                    logger.error(f"Index: {error.Index}")
            else:
                logger.info(f"Successfully created audience")
                if hasattr(response, 'AudienceIds'):
                    logger.info(f"Audience IDs: {response.AudienceIds.long}")

            return response
        except Exception as e:
            logger.error(f"Error creating audience SKD: {str(e)}")
            raise

    def get_offline_conversion_goals(self):
        try:
            response=self.campaign_service.GetConversionGoalsByIds(
                            ConversionGoalTypes="Event"
                        )
            print(response)
            if response and hasattr(response, 'ConversionGoals') and response.ConversionGoals:
                # Access the tuple containing the goals (assuming it's the first element)
                goals_tuple = response.ConversionGoals[0]
                print(f"Found {len(goals_tuple)} offline conversion goals:")
                for i, goal_obj in enumerate(goals_tuple):
                    try:
                        # Access the Name attribute directly from the goal object
                        name = getattr(goal_obj, 'Name', 'Unknown Name')
                        print(f"- {name}")
                        logger.debug(f"Processed goal {i}: {name}")
                    except Exception as e:
                        logger.error(f"Error processing goal object {i}: {str(e)}\nData: {goal_obj}")
                        print(f"Goal {i} could not be processed - check logs.")
            else:
                print("No offline conversion goals found")
        except Exception as e:
            logger.error(f"Error retrieving offline conversion goals: {str(e)}")
            raise

    def update_audience_list_sdk(self,parent_id:int,**update_fields: dict[str,Any]) -> None:
        campaign_types = self.campaign_service.factory.create('ns3:ArrayOfstring')
        campaign_types.string = ['Audience']

        customer_list = set_elements_to_none(self.campaign_service.factory.create('CustomerList'))
        customer_list.Id = parent_id
        
        if 'audience_network_size' in update_fields:
            customer_list.AudienceNetworkSize = update_fields['audience_network_size']
        if 'description' in update_fields:
            customer_list.Description = update_fields['description'] 
        if 'membership_duration' in update_fields:
            customer_list.MembershipDuration = update_fields['membership_duration']
        if 'name' in update_fields:
            customer_list.Name = update_fields['name']
        if 'search_size' in update_fields:
            customer_list.SearchSize = update_fields['search_size']
            
        customer_list.SupportedCampaignTypes = campaign_types

        try:
            audiences = set_elements_to_none(self.campaign_service.factory.create('ArrayOfAudience'))
            audiences.Audience = customer_list
            response = self.campaign_service.UpdateAudiences(Audiences=[audiences])

            if hasattr(response, 'PartialErrors') and response.PartialErrors:
                logger.error("Partial Errors:")
                for error in response.PartialErrors.BatchError:
                    logger.error(f"Error Code: {error.Code}")
                    logger.error(f"Message: {error.Message}")
                    logger.error(f"Index: {error.Index}")
            else:
                    logger.info("Successfully updated audience")
            
            return response
        except Exception as e:
            logger.error(f"Error updating audience SDK: {str(e)}")
            raise

    def get_conversion_by_tag(self):
        try:
            response = self.campaign_service.GetConversionGoalsByTagIds(
                ConversionGoalTypes=["OfflineConversion"]
            )
            print(response)
        except Exception as e:
            logger.error(f"Error retrieving conversion goals by tag: {str(e)}")
            raise
        


def main():
    try:
        manager = BingAdsManager()
        
        # Create customer lists
        customer_lists = [
            manager.create_customer_list(
                name=f"TestList {i}",
                description=f"Test Description {i}"
            )
            for i in range(10, 12)
        ]

        # Upload customer lists BULK API
        #manager.upload_customer_lists(customer_lists)

        #Create Customerlist
        manager.create_audience_sdk()

        # Retrive all customer lists
        # manager.get_all_customer_lists()

        # print all customer lists
        # for entity in manager.read_download_file('result_latest.csv'):
        #     if isinstance(entity, BulkCustomerList):
        #         print(entity.customer_list)

        # Update customer lists
        # manager.update_customer_lists(832908368, audience_network_size=50, description="Updated description", membership_duration=60, name="Updated Name", search_size=500)
        # manager.update_audience_list_sdk(832971597, audience_network_size=50, description="Updated description", membership_duration=60, name="Updated Name", search_size=500)


        # Update audience data
       # audience_data = [''.join(random.choices(string.ascii_lowercase + string.digits, k=64)) for _ in range(999)]
        # audience_data = ['93dbbd5ee9b632598cc591f6f4e894c2a081ae8ceb8c3e67356d6ecdf5d5be3c']
        #  print(audience_data)
        # manager.update_audience_data(832908368,"",action_type="Add",audience_data=audience_data)

        # manager.update_audience_data_method(832908368,"",action_type="Add",audience_data=audience_data)
        # manager.get_accounts_data()
        # manager.get_user_data()

        # manager.getUetTags()
        # manager.get_an_audience_sdk(832908368)
        # manager.get_offline_conversion_goals()
        # manager.get_all_goals()
        manager.get_conversion_by_tag()



        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        raise
    

if __name__ == "__main__":
    main()