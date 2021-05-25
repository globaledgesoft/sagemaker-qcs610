import sys
sys.path.append("./libboto3")            # Adding dependency library path 
import config
import numpy as np
import boto3
import base64
import cv2
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default = "./images/sample.jpg ", required=False, help=" Image file path for model inferencing")   
args = vars(ap.parse_args())


file_name = args['image']

endpoint_name = 'provide sagemaker model endpoint name'                   

runtime = boto3.Session().client(service_name='runtime.sagemaker',aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key , region_name= config.region) 


with open(file_name, "rb") as img:
	b64 = base64.b64encode(img.read())
    
decoded_byteimg = base64.decodebytes(b64)
img_buffer = np.frombuffer(decoded_byteimg, dtype=np.uint8)

img = cv2.imdecode(img_buffer, flags=cv2.IMREAD_COLOR)
img = cv2.resize(img, (config.imgWidth,config.imgHeight), interpolation = cv2.INTER_AREA)

img = img/255.0
arr = img.reshape((1,) + img.shape)

data = json.dumps({"instances": arr.tolist()})

response = runtime.invoke_endpoint(EndpointName=endpoint_name, 
                                   ContentType= 'application/json', 
                                   Body=data)

result = json.loads(response['Body'].read().decode())
index = np.argmax(result['predictions'][0])
print("image is classified as", config.label[index])
