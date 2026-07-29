from logger import log_info, log_warning, log_error

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import boto3

stage = "[Ingest]"

def get_s3_client():
    '''Returns AWS S3 client using credentials stored in env'''
    try:
        log_info(stage,f"Connecting to AWS S3...")
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name = 'ap-south-1'
        )
        log_info(stage,f"Connection Successful")
    except Exception as e:
        log_error(stage,f"Connection Failed: {e}")
        raise
    return s3


def download_file(bucket_name,object_key,local_path):
    '''Downloads file from AWS S3 bucket and saves to local'''
    try:
        log_info(stage,f"Downloading | {object_key} from {bucket_name}")
        s3 = get_s3_client()
        s3.download_file(bucket_name,object_key,local_path)
        log_info(stage,f"Download Successful | Saved to {local_path}")
    except Exception as e:
        log_error(stage,f"Download Failed: {e}")
        raise

def read_csv(input_local_path):
    '''Returns the contents of a csv file in form of list of dictionary rows'''
    log_info(stage,f"Reading File | {input_local_path.split('/')[-1]}")
    row_list = []
    try:
        with open(input_local_path,newline="") as f: 
            reader = csv.DictReader(f)
            for row in reader:
                row_list.append(row)
            if len(row_list) <=0:
                raise Exception("File empty")
        log_info(stage,f"Reading Successful")
    except Exception as e:
        log_error(stage,f"Reading Failed: {e}")
        raise
    return row_list, list(row_list[0].keys())