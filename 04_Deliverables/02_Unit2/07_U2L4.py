import boto3
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_path = 'C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/'
bucket_name = "raw-bucket-427763921511-ap-south-1-an"
download_file_name = "dirty/dealer.csv"
dealer_downloaded_file_path = root_path + '04_Deliverables/02_Unit2/08_dealer_downloaded.csv'

def list_bucket_objects(s3_client,bucket_name):
    '''List all objects in specified S3 bucket'''
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if "Contents" not in response:
            logger.warning(f"No objects found in {bucket_name}")
            return []
        
        for object in response.get("Contents",[]):
            logger.info(f"Found: {object['Key']}")
            
        return response["Contents"]
    except Exception as e:
        logger.error(f"Failed to list objects:{e}")
        raise

def download_from_s3(s3_client,bucket,s3_key,local_path):
    '''Download file from S3 to local filesystem'''
    try:
        logger.info(f"Downloading {s3_key} from {bucket}")
        
        s3_client.download_file(
            bucket, s3_key, local_path
        )
        
        logger.info(f"Saved to {local_path}")
        return True
    except Exception as e: 
        logger.error(f"Download failed: {e}")
        

def main(bucket_name,download_file_name,local_file_path):
    load_dotenv()
    
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name='ap-south-1'
    )
    logger.info("S3 client initialized successfully")
    
    list_bucket_objects(s3, bucket_name)
    
    download_from_s3(
        s3, bucket_name, download_file_name, local_file_path
    )
    
main(bucket_name, download_file_name, dealer_downloaded_file_path)