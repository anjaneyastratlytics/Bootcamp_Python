from logger import log_info, log_warning, log_error

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import boto3

def save_files(valid, invalid, field_names, output_clean_local_path, output_reject_local_path):
    '''Saves processed clean and reject files to local'''
    try: 
        with open(output_clean_local_path,newline="",mode="w") as f_clean, open(output_reject_local_path,newline="",mode="w") as f_reject:
            log_info(f"Saving Processed files | Clean file: {output_clean_local_path} | Reject file: {output_reject_local_path}")

            clean_writer = csv.DictWriter(f_clean,fieldnames=field_names)
            clean_writer.writeheader()
            for row in valid:
                clean_writer.writerow(row)

            reject_writer = csv.DictWriter(f_reject,fieldnames=field_names+['errors'])
            reject_writer.writeheader()
            for row in invalid:   
                reject_writer.writerow(row)

            log_info(f"Saving Successful")

    except Exception as e:
        log_error(f"Saving Failed: {e}")
        raise

def get_s3_client():
    '''Returns AWS S3 client using credentials stored in env'''
    try:
        log_info(f"Connecting to AWS S3...")
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name = 'ap-south-1'
        )
        log_info(f"Connection Successful")
    except Exception as e:
        log_error(f"Connection Failed: {e}")
        raise
    return s3

def upload_file(local_path,bucket_name,object_key):
    '''Uploads file from local and saves to AWS S3 bucket'''
    try:
        log_info(f"Uploading | {local_path}")
        s3 = get_s3_client()
        s3.upload_file(local_path,bucket_name,object_key)
        log_info(f"Upload Successful | Saved as {object_key} in {bucket_name}")
    except Exception as e:
        log_error(f"Upload Failed: {e}")
        raise
    
