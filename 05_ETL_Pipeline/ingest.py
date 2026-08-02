from config import s3_region, DB_HOST, DB_NAME, DB_USER, DB_PORT
from logger import log_info, log_warning, log_system_error
from helper import retry

import boto3
import csv
import json
import hashlib
import psycopg2

import os
from dotenv import load_dotenv
load_dotenv()

module = "[INGEST]"

@retry()
def download_from_s3(bucket_name,object_key,local_path):
    '''Downloads object from AWS S3 and saves to local'''
    log_info(module,f"Downloading from S3 | Bucket = {bucket_name} | Object = {object_key}")
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
            region = s3_region
        )
        s3.download_file(bucket_name,object_key,local_path)
        log_info(module,f"Download successful | Saved to {local_path}")
    except ConnectionError as e:
        log_system_error(module, f"Connection failed: {e}")
        raise
    except Exception as e:
        log_system_error(module,f"Unexpected error: {e}")
        raise

def generate_file_hash(file_path):
    '''Reads file content and creates unique file hash'''
    log_info(module, f"Creating hash | {file_path}")
    hasher = hashlib.sha256()
    try:
        with open(file_path,mode="rb") as f:
           hasher.update(f.read())
        log_info(module,f"Hash created successfullly")
    except Exception as e:
        log_system_error(module,f"Hashing failed: {e}")
        raise
    return hasher.hexdigest()

@retry()
def is_already_processed(file_hash):
    '''Checks if the file is already processed'''
    log_info(module, f"Initiating search in load_tracking")
    try:
        log_info(module,f"Connecting to Database")
        with psycopg2.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = DB_USER,
            password = os.getenv("DB_PASS"),
            port = DB_PORT
        ) as conn:
            log_info(module,f"Connection Successful")
            with conn.cursor() as cursor:
                query = '''SELECT 1 FROM load_tracking WHERE file_hash = %s'''
                cursor.execute(query,(file_hash,))
                if cursor.fetchone():
                    log_warning(module, "File already processed")
    except ConnectionError as e:
            log_system_error(module, f"Connection failed: {e}")
            raise
    except Exception as e:
        log_system_error(module,f"Unexpected error: {e}")
        raise

def get_rows_list_from_csv(file_path):
    '''Reads csv and returns list of dictionary rows'''
    log_info(module, f"Reading csv file | {file_path}")
    row_list = []
    try:
        with open(file_path,newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_list.append(row)
        log_info(module,f"Read {len(row_list)} rows successfullly")
    except Exception as e:
        log_system_error(module,f"Reading failed: {e}")
        raise
    return row_list

def get_rows_from_csv(file_path):
    '''Reads csv and returns dictionary rows one by one'''
    log_info(module, f"Reading csv file | {file_path}")
    try:
        with open(file_path,newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    except Exception as e:
        log_system_error(module,f"Reading failed: {e}")
        raise
    
def get_rows_list_from_jsonl(file_path):
    '''Reads jsonl and returns list of dictionary rows'''
    log_info(module,f"Reading jsonl file | {file_path}")
    row_list = []
    try:
        with open(file_path,newline="") as f:
            for line in f:
                row = json.loads(line)
                row_list.append(row)
        log_info(module,f"Read {len(row_list)} rows successfullly")
    except Exception as e:
        log_system_error(module,f"Reading failed: {e}")
        raise
    return row_list

def get_field_values(file_name,row_list,field):
    '''Returns a set of unique field values'''
    log_info(module,f"Extracting values | File = {file_name} | Field = {field}")
    value_set = set()
    for row in row_list:
        value = row.get(field)
        if value:
            value_set.add(value)
    log_info(module,f"Found {len(value_set)} unique {field}(s)")
    return value_set