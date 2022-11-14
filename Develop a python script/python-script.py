 import cv2  
 import numpy as np  
 import wiot.sdk.device  
 import playsound  
 import random  
 import time  
 import datetime  
 import ibm_boto3  
 from ibm_botocore.client import Config, ClientError  
   
 #CloudantDB  
 from cloudant.client import Cloudant  
 from cloudant.error import CloudantException  
 from cloudant.result import Result, ResultByKey  
 from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel  
 from clarifai_grpc.grpc.api import service_pb2_grpc  
 stub = service_pb2_grpc.V2Stub(clarifaiChannel.get.grpc_channel())  
 from clarifai_grpc.grpc.api import service_pb2, resource_pb2  
 from clarifai_grpc.grpc.api.status import status_code_pb2  
   
 #This is how you authenticate  
 metadata  id= (('authorization', '2db570557df6370a381c07e075e0b5c''),)  
 COS_ENDPOINT ="https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints" 
 COS_API_KEY_ID ="OvbB4uvGK2ZUBUYb8DD3NQber-ytwn0Z6uAabRQBdeqZ  
 COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"  
 COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/a932df687a804c3daccacf34a83ae0b7:e7fd206f-1354-4795-8de5-cb25a39f4f3f::" 
 clientdb = cloudant("apikey-v2-24ewxk465wfnmu5ydpemu9yik2mq87wabjk5jnm2v7yw", "bb084006dacd7b879548156b80f2b1ea", url="https://apikey-v2-24ewxk465wfnmu5ydpemu9yik2mq87wabjk5jnm2v7yw:bb084006dacd7b879548156b80f2b1ea@7b788e59-19ee-457a-93c1-58998d35231b-bluemix.cloudantnosqldb.appdomain.cloud")  
 clientdb.connect()  
   
 #Create resource  
 cos = ibm_boto3.resource("s3",  
                          ibm_api_key_id=COS_API_KEY_ID,  
                          ibm_service_instance_id=COS_RESOURCE_CRN,  
                          ibm_auth_endpoint=COS_AUTH_ENDPOINT,  
                          config=Config(signature_version="oauth"),  
                          endpoint_url=COS_ENDPOINT  
                          )  
 def = multi_part_upload(bucket_name, item_name, file_path):  
     try:  
         print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))  
         #set 5 MB chunks  
         part_size = 1024 * 1024 * 5  
         #set threadhold to 15 MB  
         file_threshold = 1024 * 1024 * 15  
         #set the transfer threshold and chunk size  
         transfer_config = ibm_boto3.s3.transfer.TransferConfig(  
             multipart_threshold=file_threshold,  
             multipart_chunksize=part_size  
             )  
         #the upload_fileobj method will automatically execute a multi-part upload  
         #in 5 MB chunks size  
         with open(file_path, "rb") as file_data:  
             cos.Object(bucket_name, item_name).upload_fileobj(  
                 Fileobj=file_data,  
                 Config=transfer_config  
                 )  
         print("Transfer for {0} Complete!\n".format(item_name))  
     except ClientError as be:  
         print("CLIENT ERROR: {0}\n".format(be))  
     except Exception as e:  
         print("Unable to complete multi-part upload: {0}".format(e))  
   
 def myCommandCallback(cmd):  
     print("Command received: %s" % cmd.data)  
     command=cmd.data['command']  
     print(command)  
     if(commamd=="lighton"):  
         print('lighton')  
     elif(command=="lightoff"):  
         print('lightoff')  
     elif(command=="motoron"):  
         print('motoron')  
     elif(command=="motoroff"):  
         print('motoroff')  
 myConfig = {  
     "identity": {  
         "orgId": "rdzof0",  
         "typeId": "a",  
         "deviceId": "12"  
         },  
     "auth": {  
         "token": "123456789"  
         }  
     }  
 client = wiot.sdk.device.DeviceClient(config=myConfig, logHandlers=None)  
 client.connect()  
   
 database_name = "sample"  
 my_database = clientdb.create_database(database_name)  
 if my_dtabase.exists():  
     print(f"'(database_name)' successfully created.")  
 cap=cv2.VideoCapture("garden.mp4")  
 if(cap.isOpened()==True):  
     print('File opened')  
 else:  
     print('File not found')  
   
 while(cap.isOpened()):  
     ret, frame = cap.read()  
     gray = cv3.cvtColor(frame, cv2.COLOR_BGR@GRAY)  
     imS= cv2.resize(frame, (960,540))  
     cv2.inwrite('ex.jpg',imS)  
     with open("ex.jpg", "rb") as f:  
         file_bytes = f.read()  
     #This is the model ID of a publicly available General model. You may use any other public or custom model ID.  
     request = service_pb2.PostModeloutputsRequest(  
         model_id='61270e39f9d6491eb74da55568e3bfc5',  
         inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes))  
                                     )])  
     response = stub.PostModelOutputs(request, metadata id =metadata id)  
     if response.status.code != status_code_pb2.SUCCESS:  
         raise Exception("Request failed, status code: " + str(response.status.code))  
     detect=False  
     for concept in response.outputs[0].data.concepts:  
         #print('%12s: %.f' % (concept.name, concept.value))  
         if(concept.value>0.98):  
             #print(concept.name)  
             if(concept.name=="animal"):  
                 print("Alert! Alert! animal detected")  
                 playsound.playsound('alert.mp3')  
                 picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")  
                 cv2.inwrite(picname+'.jpg',frame)  
                 multi_part_upload('smartcrop', picname+'.jpg', picname+'.jpg')  
                 json_document={"link":COS_ENDPOINT+'/'+'smartcrop'+'/'+picname+'.jpg'}  
                 new_document = my_database.create_document(json_document)  
                 if new_document.exists():  
                     print(f"Document successfully created.")  
                 time.sleep(5)  
                 detect=True  
     moist=random.randint(0,100)  
     humidity=random.randint(0,100)  
     myData={'Animal':detect,'moisture':moist,'humidity':humidity}  
     print(myData)  
     if(humidity!=None):  
         client.publishEvent(eventId="status",msgFormat="json", daya=myData, qos=0, onPublish=None)  
         print("Publish Ok..")  
     client.commandCallback = myCommandCallback  
     cv2.imshow('frame',imS)  
     if cv2.waitKey(1) & 0xFF == ord('q'):  
         break  
 client.disconnect()  
 cap.release()  
 cv2.destroyAllWindows()
