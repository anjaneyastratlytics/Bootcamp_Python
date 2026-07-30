from config import DB_HOST, DB_NAME, DB_USER
from logger import log_info, log_warning, log_error

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import boto3
import psycopg2

stage = "[Load]"

def save_files(valid, invalid, field_names, output_clean_local_path, output_reject_local_path):
    '''Saves processed clean and reject files to local'''
    try: 
        with open(output_clean_local_path,newline="",mode="w") as f_clean, open(output_reject_local_path,newline="",mode="w") as f_reject:
            log_info(stage,f"Saving Processed files | Clean file: {output_clean_local_path} | Reject file: {output_reject_local_path}")

            clean_writer = csv.DictWriter(f_clean,fieldnames=field_names)
            clean_writer.writeheader()
            for row in valid:
                clean_writer.writerow(row)

            reject_writer = csv.DictWriter(f_reject,fieldnames=field_names+['errors'])
            reject_writer.writeheader()
            for row in invalid:   
                reject_writer.writerow(row)

            log_info(stage,f"Saving Successful")

    except Exception as e:
        log_error(stage,f"Saving Failed: {e}")
        raise


def upload_file(local_path,bucket_name,object_key):
    '''Uploads file from local and saves to AWS S3 bucket'''
    try:
        log_info(stage,f"Uploading | {local_path}")
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name = 'ap-south-1'
        )
        s3.upload_file(local_path,bucket_name,object_key)
        log_info(stage,f"Upload Successful | Saved as {object_key} in {bucket_name}")
    except Exception as e:
        log_error(stage,f"Upload Failed: {e}")
        raise

def record_load(file_name,file_hash):
    '''Records processed files in load_tracking_table'''
    log_info(stage, "Recording file in load_tracking...")
    try:
        log_info(stage,"Connecting to Database...")
        conn = psycopg2.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = DB_USER,
            password = os.getenv("DB_PASS"),
            port = 5432
        )
        log_info(stage, "Connection Successful")
    except Exception as e:
        log_error(stage, f"Failed to connect: {e}")
        raise

    with conn.cursor() as cursor:
        query = '''INSERT INTO load_tracking(file_name,file_hash) VALUES (%s,%s)'''
        log_info(stage, f"Executing Query | {query}")
        try:    
            cursor.execute(query,(file_name,file_hash))
            conn.commit()
            log_info(stage,"Recording Successful")
        except Exception as e:
            log_error(stage, f"Recording failed: {e}")
            raise

    conn.close()
