from config import DB_HOST, DB_NAME, DB_USER
from logger import log_info, log_warning, log_error

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import boto3
import hashlib
import psycopg2

stage = "[Ingest]"

def download_file(bucket_name,object_key,local_path):
    '''Downloads file from AWS S3 bucket and saves to local'''
    try:
        log_info(stage,f"Downloading | {object_key} from {bucket_name}")

        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name = 'ap-south-1'
        )
        
        s3.download_file(bucket_name,object_key,local_path)
        log_info(stage,f"Download Successful | Saved to {local_path}")
    except Exception as e:
        log_error(stage,f"Download Failed: {e}")
        raise

def generate_file_hash(file_path):
    '''Creates SHA256 hash for file content'''
    log_info(stage,f"Reading File | {file_path.split('/')[-1]}")
    hasher = hashlib.sha256()
    try:
        with open(file_path,mode="rb") as f: 
            hasher.update(f.read())
        file_hash = hasher.hexdigest()
        log_info(stage,f"Hash Created: {file_hash}")
        return file_hash
    except Exception as e:
        log_error(stage,f"Hashing Failed: {e}")
        raise

def is_already_processed(file_hash):
    '''Checks if file has already been processed'''
    log_info(stage, f"Checking if file processed earlier...")
    try:
        log_info(stage, f"Connecting to Database...")
        conn = psycopg2.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = DB_USER,
            password = os.getenv("DB_PASS"),
            port = 5432
        )
        log_info(stage, f"Connection Successful...")
    except Exception as e:
        log_error(stage, f"Failed to connect: {e}")
        raise

    with conn.cursor() as cursor:
        query = "SELECT 1 FROM load_tracking WHERE file_hash = %s"
        log_info(stage, f"Executing Query | {query}")
        try:
            cursor.execute(query, (file_hash,))
            processed = cursor.fetchone() is not None
        except Exception as e:
            log_error(stage, f"Execution failed: {e}")
            raise
    
    if processed:
        log_warning(stage, f"File processed already")
    else:
        log_info(stage, f"File not processed")

    conn.close()
    return processed

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