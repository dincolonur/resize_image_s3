# Resize Image in AWS S3

This project is designed to resize images from the source AWS s3 bucket and write into the target AWS S3 bucket. <br> <br>
<b>Main function: </b>  <br> 
      - Reads from source bucket in the input partition  <br>
      - resize the images & create thumbnails  <br>
      - POST the resized image to API URL  <br>
      - Upload the resized images to the target bucket  <br>
      - Upload the thumbnail images to the target bucket  <br>


<br>

<b>For API</b> , we used Flask application. <br>
Flask App source code is in flask/app_base64.py script. <br>
To start the Flask app, please run the following code; <br>
```
python3 flask/app_base64.py
```

<br>

<b>For AWS</b> , please use the secrets.json file and update the credentials; <br>

```
{
    "region_name": "region_name_value",
    "aws_access_key_id": "aws_access_key_id_value",
    "aws_secret_access_key": "aws_secret_access_key_value"
}
```
<br>
<b>Example Usage:</b>

```
Resize Image Application

options:
  -h, --help  show this help message and exit
  -p P        Partition to be processed
  -s S        Source Bucket Name
  -t T        Target Bucket Name
  -r R        Resize dimensions int,int
  -u U        API url to POST resized Image

Example Usage:

python3 operation/main.py -p folder_1 -s source_bucket_name -t source_bucket_name -r 500,500 -u http://127.0.0.1:5000/im_size

```



