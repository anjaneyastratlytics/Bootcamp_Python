import boto3
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_path = 'C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/'
bucket_name = "raw-bucket-427763921511-ap-south-1-an"
clean_dealer_file_path = root_path + '01_Data/clean/dealer.csv'
upload_s3_key = "processed/dealer_clean.csv"

def upload_to_s3(s3_client,local_path,bucket,s3_key):
    '''Upload local file to s3 bucket'''
    
    try:
        logger.info(f"Uploading {local_path} to s3://{bucket}/{s3_key}")
        
        s3_client.upload_file(
            local_path, bucket, s3_key
        )
        
        logger.info(f"Upload successful: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return False

def main(upload_file_path, bucket_name, upload_s3_key):
    load_dotenv()
    
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name='ap-south-1'
    )
    logger.info("S3 client initialized successfully")
    
    upload_to_s3(
        s3,
        upload_file_path,
        bucket_name,
        upload_s3_key
    )
    
main(clean_dealer_file_path, bucket_name, upload_s3_key)