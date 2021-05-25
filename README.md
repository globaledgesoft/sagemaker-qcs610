# Sagemaker application deployment on the qcs-610
## About the project
   - In this project, one can use Amazon’s sagemaker to create and deploy the custom image classification model on the cloud instance as an endpoint and invoke the same to the target board and perform inference on the target Board
     
## Dependencies
- Ubuntu System 18.04 or above
- Install Adb tool (Android debugging bridge) on host system
- create an Aws user account
- Install python3.5 or above on the host system 

## Prerequisites
- Camera Environment configuration setup on the target device.
- Create a Amazon sagemaker Notebook Instance. 
- Create a  s3 bucket service on AWS website.
- Building the opencv library for target board.
- Building the boto3 library for target board.
- keras image classification model


### Camera Environment configuration setup on the target device.
 -To setup the camera environment configuration follow the below  document "Turbox-C610_Open_Kit_Software_User_Manual_LE1.0_v2.0.pdf" In given url 
“https://www.thundercomm.com/app_en/product/1593776185472315” and Refer section 2.10.1

### Create an Amazon Sagemaker Notebook Instance
  - To create a amzon sagemaker notebook instance refer below link 
  ```
    https://docs.aws.amazon.com/sagemaker/latest/dg/gs-setup-working-env.html
  ```  
 Once the setup notbook instance is done, note down the sagemaker role name.

### Create a s3 bucket service on Aws website
   - To create the s3 bucket, refer below url from amazon document. 
   ```sh
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html
   ```
**Note:** once the s3 bucket is created, note down the bucket name.

### Install opencv library on board 
- To install opencv library on the target board the required meta recipe for opencv is already present in folder “poky/meta-openembedded/meta-oe/recipes-support/opencv/opencv_3.4.5.bb” file. We need to follow the below steps to build.

-  Get into the yocto working directory

 ```sh
  $ cd  <yocto working directory>
 ```
 
- Execute source command for environment setting 

 ```sh
    $ source poky/qti-conf/set_bb_env.sh
 ```
- The pop up menu will be open for available machines that select “qcs610-odk” and press ok. Then one more pop up window will be open for distribution selection in that we need to select “qti-distro-fullstack-perf”. Run the bitbake command for installing packages.

 ```sh
 $ bitbake opencv 
 ```
 
- Once the build is complete the shared library and include file will be available in “./tmp-glibc/sysroots-components/armv7ahf-neon/opencv/usr”
Push the opencv shared library to the target board 

 ```sh
   $ cd  ./tmp-glibc/sysroots-components/armv7ahf-neon/opencv/usr/
   $ adb push lib/  /data/sagemaker/
   $ adb push include/opencv2 /usr/include/
   $ adb push include/opencv /usr/include/
 ```

**Note**: 
- For more reference refer to the “QCS610/QCS410 Linux Platform Development Kit Quick Start Guide document”.
- Also make sure install the all the dependency library from the yocto build to the system (ex: libgphoto2, libv4l-utils) 
- bb recipes of above  library are available inside meta-oe layer, you can directly run bitbake command


### Install boto3 library on board
 To install the boto3 package on qcs610. you need to build and install the following python3 packages on yocto build. below are the list of packages
     
   - python3-boto3
   - python3-botocore
   - python3-jmespath 
   - python3-s3transfer
   - html
   - date-util
   - multiprocessing
   - concurrent.

We can place the above mentioned bb recipe in the given folder name "poky/poky/meta-openembedded/meta-python/python/". Meta recipes for these packages are available in the meta-recipe folder from given source repository. Afterwards, run the bitbake command for each library, for example for python3-boto3 package run below command

   ```sh
     $ bitbake python3-boto3
   ``` 

Once the build is complete for all recipes, create a libboto3 directory and copy all the required libraries to the folder, 

push this same folder to /data/sagemaker folder path of target board.
 ```sh 
    $  adb push libboto3/ /data/sagemaker/ 
 ```

### Steps to build and run the application: 

 To Deploy the custom model on sagemaker notebook and inference the endpoint on target board, follow below steps.
 
**Step-1** : Upload the files to the sagemaker notebook instance and create endpoint.
  -  clone the source repository on the host system(local system)
  ```sh
       $ git clone <source repository> 
       $ cd <source repository>
  ```
  -  copy the keras model file to the repo directory
  ```sh
       $ cp keras_model/model.h5 <source_repository>
  ```
  - This repository contains the model files, python notebook file and  config file for deploy model. To upload and execute it on notebook instance follow below steps

    - Access the SageMaker notebook instance you created earlier on aws.
    - To upload the files, click the Upload button on the right. Then in the file selection popup, select the  “sagemaker_deployment.ipynb” file from the folder on your host system. Click the blue Upload button that appears to the right of the notebook’s file name.
    - Repeat this step for config.py, train.py and keras model file(model.h5)  to be upload.
    - You are now ready to begin the notebook. Click the notebook’s file  to open in conda_tensorflow_p36 environment. Execute the notebook instance.
    - After completion of execution endpoint will be generated 
    - Note down the sagemaker end point name from aws sagemaker console.

**Note**: Before uploding to notebook instance, make sure, in the file config.py file, you need to fill following details

      - aws_access_key_id,
      - aws_secret_access_key,
      - aws_region,
      - sagemaker Execution RoleName,
      - Image cassification model class labels information,
      - required input width and height for the given model.

- For more information, please refer the below url "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html"


**Step-2** : initialize the target board with root access.
  ```sh
       $ adb root 
       $ adb remount 
       $ adb shell  mount -o remount,rw /
  ```

**Step-3** : Push the source to the target board with adb command.
     -  Edit the inference.py file and provide the endpoint instance details in endpoint_name field
     - Upload the inference.py and config.py file to the target board from host system  

 ```sh               

       $ adb push inference.py  /data/sagemaker/
       $ adb push config.py  /data/sagemaker/
       $ adb push images/ /data/sagemaker/
  ```
    
**Step-4** : Execute the python script in the target environment.
  - To start the application, run the below commands on the qcs610 board, 
   ```sh
       /# adb shell
       /# 
   ```
    To enable wifi connectivity on target board

   ```sh        
       /# wpa_supplicant -Dnl80211 -iwlan0 -c /etc/misc/wifi/wpa_supplicant.conf -ddddt &
       /# dhcpcd wlan0
   ```  
    
   Export the shared library to the LD_LIBRARY_PATH
      
   ```sh  
        /# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/sagemaker/lib/ 
        /# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/sagemaker/libboto3/
        /# cd data/sagemaker/
        update the date in the qcs610 board with current timing
		/# date -s '2021-05-11 12:28:00'
   ```
   
**Step 4**:  Execute the python code on the target board,

   ```sh  
         /# python3 inference.py  -i images/sample.jpg   
   ```         

- it will start invoking endpoint adn perfor inferencing and display the output predicted class on the target board terminal.

**Note**: once the sagemaker experment is done, delete the created resource on aws sagemaker to avoid charges. Following resources need to be deleted 

     -  Endpoint,
     -  Endpoint configuration
     -  model data
     -  notebook instance
     -  cloud watch logs
     -  s3 storage 


