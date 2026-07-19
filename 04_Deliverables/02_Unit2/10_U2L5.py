import csv
import json
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import boto3

root_path = 'C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/'
log_file_path = root_path + '04_Deliverables/02_Unit2/11_pipeline.log'
bucket_name = 'raw-bucket-427763921511-ap-south-1-an'
input_object_key =  'dirty/dealer.csv'
input_local_path = root_path + '04_Deliverables/02_Unit2/12_dirty_dealer.csv'
output_clean_local_path = root_path + '04_Deliverables/02_Unit2/13_clean_dealer.csv'
output_reject_local_path = root_path + '04_Deliverables/02_Unit2/14_reject_dealer.csv'
output_clean_object_key = 'processed/clean/dealer.csv'
output_reject_object_key = 'processed/reject/dealer.csv'

import logging
logging.basicConfig(
    filename = log_file_path,
    filemode = 'a',
    level = logging.INFO,
    format ="%(asctime)s %(levelname)s %(message)s"
)

def get_s3_client():
    '''Returns AWS S3 client using credentials stored in env'''
    try:
        logging.info(f"Connecting to AWS S3...")
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name = 'ap-south-1'
        )
        logging.info(f"Connection Successful")
    except Exception as e:
        logging.error(f"Connection Failed: {e}")
        raise
    return s3


def download_file(bucket_name,object_key,local_path):
    '''Downloads file from AWS S3 bucket and saves to local'''
    try:
        logging.info(f"Downloading | {object_key} from {bucket_name}")
        s3 = get_s3_client()
        s3.download_file(bucket_name,object_key,local_path)
        logging.info(f"Download Successful | Saved to {local_path}")
    except Exception as e:
        logging.error(f"Download Failed: {e}")
        raise


def read_csv(input_local_path):
    '''Returns the contents of a csv file in form of list of dictionary rows'''
    logging.info(f"Reading File | {input_local_path.split('/')[-1]}")
    row_list = []
    try:
        with open(input_local_path,newline="") as f: 
            reader = csv.DictReader(f)
            for row in reader:
                row_list.append(row)
        logging.info(f"Reading Successful")
    except Exception as e:
        logging.error(f"Reading Failed: {e}")
        raise
    return row_list


def normalize_null(value):
    '''Normalizes null meaning value to standardized python None'''
    if value is None or not isinstance(value,str):
        return value
    value = value.strip()
    if value.lower() in {'none','null','nan','na','n/a',''}:
        return None
    return value

def get_normalized_rows(row_list):
    '''Returns entire row list after normalizing null for all fields of all rows'''
    logging.info("Normalizing Null Values")
    for idx in range(len(row_list)):
        row = row_list[idx]
        for field in row:
            row_list[idx][field] = normalize_null(row.get(field))
    return row_list


def check_required_fields(row):
    '''Checks if the row contains all required fields'''
    required = ['dealer_id','dealer_code','dealer_name','region','dealer_type','created_date','is_active','credit_terms_days']
    errors = []
    for field in required:
        if not row.get(field):
            errors.append(("E001",f"Missing Required Field ({field})"))
    return errors

def validate_field_types_and_values(row):
    '''Checks specific field types, formats, and values as per predefined rules and returns validated row'''
    errors = []

    int_fields = ['dealer_id','credit_terms_days']
    for field in int_fields:
        if not row.get(field):
            continue
        try:
            row[field] = int(row.get(field))
        except(TypeError,ValueError):
            errors.append(("E002", f"Invalid {field} type"))

    date_fields = ['created_date']
    for field in date_fields:
        if not row.get(field):
            continue
        try:
            row[field] = datetime.strptime(row.get(field),'%Y-%m-%d')
        except(TypeError,ValueError):
            errors.append(("E003", f"Invalid {field} format"))

    valid_regions = {'NORTH','SOUTH','EAST','WEST'}
    region = row.get('region')
    if region:
        row[field] = region.upper()
    if region and region not in valid_regions:
        errors.append(("E004", f"Invalid {field} value"))    

    return row, errors

def validate_rows(row_list):
    '''Runs all predefined validations together'''
    error_summary = {
        "E001": {
            'description': "Missing Required Fields",
            'count': 0
        },
        "E002": {
            'description': "Invalid Integer Field(s) Type",
            'count': 0
        },
        "E003": {
            'description': "Invalid Date Field(s) Format",
            'count': 0
        },
        "E004": {
            'description': "Invalid Region Value",
            'count': 0
        }
    }
    valid = []
    invalid = []
    row_count = 0
    for row in row_list:
        row_count += 1
        logging.info(f"Validating row | Row Number: {row_count} | dealer_id: {row.get('dealer_id')}")
        errors = []

        mising_errors = check_required_fields(row)
        errors.extend(mising_errors)

        validated_row, val_errors = validate_field_types_and_values(row)
        errors.extend(val_errors)

        if errors:
            error_codes = set([e[0] for e in errors])
            error_descs = [e[1] for e in errors]
            logging.error(f"Errors found: {error_descs}")
            for code in error_codes:
                error_summary[code]['count'] += 1
            validated_row['errors'] = error_descs
            invalid.append(validated_row)
        else:
            logging.info(f"No errors found")
            valid.append(validated_row)

    return valid, invalid, error_summary

def log_validation_summary(clean_cnt,reject_cnt,error_summary):
    '''Logs Validation Summary'''
    total_cnt = clean_cnt + reject_cnt
    clean_pct = round(100.0*clean_cnt/total_cnt,2)
    reject_pct = round(100.0*reject_cnt/total_cnt,2)
    logging.info(f"Validation Summary:\n1. Total rows processed = {total_cnt}\n2. Clean rows = {clean_cnt} ({clean_pct} %)\n3. Reject rows = {reject_cnt} ({reject_pct} %)\n4. Error Summary:\n{json.dumps(error_summary,indent=4)}")

def save_files(valid, invalid, field_names, output_clean_local_path, output_reject_local_path):
    '''Saves processed clean and reject files to local'''
    try: 
        with open(output_clean_local_path,newline="",mode="w") as f_clean, open(output_reject_local_path,newline="",mode="w") as f_reject:
            logging.info(f"Saving Processed files | Clean file: {output_clean_local_path} | Reject file: {output_reject_local_path}")

            clean_writer = csv.DictWriter(f_clean,fieldnames=field_names)
            clean_writer.writeheader()
            for row in valid:
                clean_writer.writerow(row)

            reject_writer = csv.DictWriter(f_reject,fieldnames=field_names+['errors'])
            reject_writer.writeheader()
            for row in invalid:   
                reject_writer.writerow(row)

            logging.info(f"Saving Successful")

    except Exception as e:
        logging.error(f"Saving Failed: {e}")
        raise

def upload_file(local_path,bucket_name,object_key):
    '''Uploads file from local and saves to AWS S3 bucket'''
    try:
        logging.info(f"Uploading | {local_path}")
        s3 = get_s3_client()
        s3.upload_file(local_path,bucket_name,object_key)
    except Exception as e:
        logging.error(f"Upload Failed: {e}")
        raise
    logging.info(f"Upload Successful | Saved as {object_key} in {bucket_name}")

def main():
    '''Orchestrates the entire pipeline'''

    # Download file from AWS S3 bucket
    download_file(bucket_name,input_object_key,input_local_path)

    # Read downloaded files and normalize
    row_list = read_csv(input_local_path)
    field_names = list(row_list[0].keys())
    norm_row_list = get_normalized_rows(row_list)

    # Data validation and clean-reject segregation
    valid, invalid, error_summary = validate_rows(norm_row_list)
    log_validation_summary(len(valid),len(invalid),error_summary)
    save_files(valid, invalid, field_names, output_clean_local_path, output_reject_local_path)

    # Upload processed files to AWS S3 bucket
    upload_file(output_clean_local_path,bucket_name,output_clean_object_key)
    upload_file(output_reject_local_path,bucket_name,output_reject_object_key)

if __name__=='__main__':
    main()

