import logging
import boto3
import os
def download_from_s3(bucket,key):
    try:
        logging.info(f"Downloading file from S3 | Bucket = {bucket} | Object = {key}")
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name = 'ap-south-1'
        )
        response = s3.download_file(bucket,key,key)
        logging.info(f"Download successful | Saved as {key}")
        return key
    except Exception as e:
        logging.info(f"Download failed: {e}")
        raise