import csv
import json
import pprint
import numpy as np
import pandas as pd

# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"

ip_sales_log_file_path = root_path + "01_Data/dirty/sales_logs.jsonl"

def normalize_null(value):
    '''Normalizes Null and missing values to None type'''
    if value is None:
        return None

    value = value.strip()
    
    if value.lower() in {"","na","null","nan"}:
        return None
    
    return value

def safe_int(value):
    '''Safely type casts integer values'''
    try:
        return int(value)
    except(ValueError, TypeError):
        return None
    
def safe_float(value):
    '''Safely type casts float values'''
    try:
        return float(value)
    except(ValueError, TypeError):
        return None
    
class DataValidationError(Exception):
    pass

def validate_record(record):
    '''Validates records to check missing product_id'''
    if not record.get("product_id"):    
        raise DataValidationError("Missing product_id")

def process_logs(file_path):
    '''Processes individual log lines separately'''

    total = 0
    parsed = 0
    skipped = 0
    failed = 0

    with open(file_path) as sales:
        print("[INFO] Parsing sales jsonl file...")

        for line in sales:
            total += 1
            try:
                record = json.loads(line)
                validate_record(record)
                parsed += 1
            except json.JSONDecodeError:
                skipped += 1
                print(f"[ERROR]: Couldn't read JSONL file line number {total}")
                continue
            except DataValidationError as e:
                failed += 1
                print(f"[ERROR]: {e} for log with event_id: {record.get('event_id')}")

    print(f"Total JSONL lines: {total}\nParsed records: {parsed}\nSkipped malformed records: {skipped}\nData validation errors: {failed}")

# --------------------------------------------Main----------------------------------------------

process_logs(ip_sales_log_file_path)