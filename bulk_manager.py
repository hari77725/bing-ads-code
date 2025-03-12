from bingads.authorization import AuthorizationData
from bingads.v13.bulk import BulkServiceManager, SubmitDownloadParameters, BulkFileReader, BulkFileWriter, BulkCustomerList, ResultFileType, FileUploadParameters
from bingads.authorization import OAuthDesktopMobileAuthCodeGrant
from bingads.service_client import ServiceClient
from main import set_elements_to_none

DEVELOPER_TOKEN = 'BBD37VB98'
ACCOUNT_ID = '526065840'
CUSTOMER_ID = '355788527'
CLIENT_ID='4c0b021c-00c3-4508-838f-d3127e8167ff'
CLIENT_STATE='ClientStateGoesHere'

def read_entities_from_bulk_file(file_path, result_file_type, file_type):
    with BulkFileReader(file_path=file_path, result_file_type=result_file_type, file_type=file_type) as reader:
        for entity in reader:
            yield entity

def write_entities_and_upload_file(bulk_service_manager, upload_entities):
    # Writes the specified entities to a local file and uploads the file. We could have uploaded directly
    # without writing to file. This example writes to file as an exercise so that you can view the structure 
    # of the bulk records being uploaded as needed. 
    writer=BulkFileWriter('./abc.csv')
    for entity in upload_entities:
        writer.write_entity(entity)
    writer.close()

    file_upload_parameters=FileUploadParameters(
        result_file_directory='./',
        compress_upload_file=True,
        result_file_name='result.csv',
        overwrite_result_file=True,
        upload_file_path='./abc.csv',
        rename_upload_file_to_match_request_id=False,
        response_mode='ErrorsAndResults'
    )
    
    def output_percent_complete(progress):
        print("Percent Complete: {0}".format(progress.percent_complete))

    bulk_file_path=bulk_service_manager.upload_file(file_upload_parameters, progress=output_percent_complete)

    download_entities=[]
    entities_generator=read_entities_from_bulk_file(file_path=bulk_file_path, result_file_type=ResultFileType.upload, file_type='Csv')
    for entity in entities_generator:
        download_entities.append(entity)

    return download_entities

def main():
    # try:
        # Validate developer token
        if not DEVELOPER_TOKEN or len(DEVELOPER_TOKEN) < 8:
            raise ValueError("Invalid developer token")

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

        bulk_service_manager = BulkServiceManager(
            authorization_data=authorization_data, 
            poll_interval_in_milliseconds=5000, 
            environment='sandbox'
        )  # Removed extra comma that was causing a tuple


    ## List download 
    #     submit_download_parameters = SubmitDownloadParameters(
    #         data_scope=['EntityData'],
    #         download_entities=['CustomerLists'],
    #         file_type='Csv',
            
    #     )
        
    #     bulk_operation = bulk_service_manager.submit_download(submit_download_parameters)
        
    #     if not bulk_operation:
    #         raise Exception("Failed to submit download operation")

    #     download_status = bulk_operation.track(timeout_in_milliseconds=3600000)
        
    #     if download_status.status != 'Completed':
    #         raise Exception(f"Download failed with status: {download_status.status}")

    #     result_file_path = bulk_operation.download_result_file(
    #         result_file_directory="./", 
    #         result_file_name='test.csv', 
    #         decompress=True, 
    #         overwrite=True,
    #         timeout_in_milliseconds=3600000
    #     )
        
    #     print("Download result file: {0}".format(result_file_path))

    # except ValueError as val_err:
    #     print(f"Validation Error: {val_err}")
    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")
    # finally:
    #     # Clean up resources if needed
    #     pass


    ## List read 

        # download_entities = []
        # res_entities = read_entities_from_bulk_file('test.csv',ResultFileType.upload, 'Csv')
        # for entity in res_entities:
        #     download_entities.append(entity)
        
        # for entity in download_entities:
        #     if(isinstance(entity, BulkCustomerList)):
        #         print(entity.customer_list)
    
    # ## upload entity
    #     upload_entities = []

    # ## Campaign service
 
    #     campaign_service= ServiceClient(
    #     service='CampaignManagementService', 
    #     version=13,
    #     authorization_data=authorization_data, 
    #     environment='sandbox',
    # )

    #     bulk_customer_list = BulkCustomerList()
    #     customer_list = set_elements_to_none(campaign_service.factory.create('CustomerList'))
    #     customer_list.AudienceNetworkSize = 30
    #     customer_list.Description = "ValueHere"

    #     customer_list.Id = None
    #     customer_list.MembershipDuration = 30
    #     customer_list.Name = "testbysdk"
    #     customer_list.ParentId = 526065840
    #     customer_list.Scope = "Customer"
    #     customer_list.SearchSize = 300
    #     customer_list.SupportedCampaignTypes = campaign_service.factory.create('ns3:ArrayOfstring').string.append("Audience")
    #     customer_list.Type = "CustomerList"
    #     bulk_customer_list.customer_list = customer_list
    #     upload_entities.append(bulk_customer_list)

    #     bulk_customer_list2 = BulkCustomerList()
    #     customer_list2 = set_elements_to_none(campaign_service.factory.create('CustomerList'))
    #     customer_list2.AudienceNetworkSize = 30
    #     customer_list2.Description = "Second customer list"
    #     customer_list2.Id = None
    #     customer_list2.MembershipDuration = 30
    #     customer_list2.Name = "testbysdk2"
    #     customer_list2.ParentId = 526065840
    #     customer_list2.Scope = "Customer"
    #     customer_list2.SearchSize = 300
    #     customer_list2.SupportedCampaignTypes = campaign_service.factory.create('ns3:ArrayOfstring').string.append("Audience")
    #     customer_list2.Type = "CustomerList"
    #     bulk_customer_list2.customer_list = customer_list2
    #     upload_entities.append(bulk_customer_list2)

    #     bulk_customer_list3 = BulkCustomerList()
    #     customer_list3 = set_elements_to_none(campaign_service.factory.create('CustomerList'))
    #     customer_list3.AudienceNetworkSize = 30
    #     customer_list3.Description = "Third customer list"
    #     customer_list3.Id = None
    #     customer_list3.MembershipDuration = 30
    #     customer_list3.Name = "testbysdk3"
    #     customer_list3.ParentId = 526065840
    #     customer_list3.Scope = "Customer"
    #     customer_list3.SearchSize = 300
    #     customer_list3.SupportedCampaignTypes = campaign_service.factory.create('ns3:ArrayOfstring').string.append("Audience")
    #     customer_list3.Type = "CustomerList"
    #     bulk_customer_list3.customer_list = customer_list3
    #     upload_entities.append(bulk_customer_list3)

    #     download = write_entities_and_upload_file(bulk_service_manager, upload_entities)
    #     for entity in download:
    #         if(isinstance(entity, BulkCustomerList)):
    #             print(entity.customer_list)

        


    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()