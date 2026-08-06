from config import DB_HOST,DB_NAME,DB_USER,DB_PORT,DB_PASS
from config import field_names_dict, postgres_load_queries, batch_size_dict
from logger import log_info,log_warning,log_system_error
from helper import retry

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import psycopg2
import json

module = "[LOAD]"

def save_to_local_csv(file_name,row_list,local_path):
    '''Takes list of row dictionaries and saves as csv file locally'''
    log_info(module,f"Saving {file_name} to local")

    if not row_list:
        log_warning(module,f"Provided row list is empty")
        return
    
    file = file_name.split('.')[0].split('_')[-1]
    field_names = field_names_dict.get(file).copy()
    if row_list[0].get('error'):
        field_names.append('error')

    try:
        with open(local_path,mode="w") as f:
            writer = csv.DictWriter(f,fieldnames=field_names)
            writer.writeheader()
            for row in row_list:
                writer.writerow(row)
        log_info(module,f"Saved at {local_path}")

    except Exception as e:
        log_system_error(module,f"Unexpected error: {e}")
        raise

def save_to_local_json(file_name,dictionary,local_path):
    '''Takes dictionary and saves as json file locally'''

    try:
        log_info(module,f"Saving {file_name} to local")
        with open(local_path,mode="w") as f:
            json.dump(dictionary,f,indent=4)
        log_info(module,f"Saved to {local_path}")

    except Exception as e:
            log_system_error(module,f"Unexpected error: {e}")

@retry()
def get_db_connection():
    '''Returns Database connection object'''

    try:
        log_info(module,f"Connecting to database")
        conn = psycopg2.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = DB_USER,
            password = DB_PASS,
            port = DB_PORT
        )
        log_info(module,f"Connection successful")

    except ConnectionError as e:
        log_system_error(module,f"Connection Failed: {e}")
        raise

    except Exception as e:
        log_system_error(module,f"Unexpected Error: {e}")   
        raise 

    return conn


def load_to_database(file_name, row_list):
    '''Takes list of row dictionaries and loads into database'''
    log_info(module,f"Loading {file_name} to database")

    if not row_list:
        log_warning(module,f"Provided row list is empty")
        return
    
    file = file_name.split('.')[0].split('_')[-1]
    field_names = field_names_dict.get(file).copy()
    values_tuple_list = [tuple([row.get(field) for field in field_names]) for row in row_list]
    query = postgres_load_queries.get(file)
    batch_size = batch_size_dict.get(file)
    
    total_cnt = len(row_list)
    if not batch_size:
        batch_size = total_cnt   
    insert_cnt = 0

    conn = get_db_connection() 
    with conn.cursor() as cursor:
        for i in range(0,total_cnt,batch_size):
            batch_no = (i/batch_size) + 1
            try:
                log_info(module,f"Batch {batch_no} transaction begin")
                batch = values_tuple_list[i:i+batch_size]
                cursor.executemany(query,batch)
                conn.commit()
                insert_cnt += len(batch)
                log_info(module,f"Transaction successful | Inserted {len(batch)} row(s)")

            except Exception as e:
                log_warning(module,f"Transaction failed: {e}")
                conn.rollback()
                log_info(module,f"Transaction rolled back")

    conn.close()

    return {
        'inserted_rows': insert_cnt,
        'failed_rows': total_cnt-insert_cnt
    }

def record_for_audit(record):
    '''Records etl metadata onto database for audit'''
    log_info(module,f"Recording etl metadata | {record.get('file_name')}")
    
    field_names = field_names_dict.get("etl_audit").copy()
    values_tuple = tuple([record[field] for field in field_names])

    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = postgres_load_queries.get("etl_audit")

        try:
            cursor.execute(query,values_tuple)
            conn.commit()
            log_info(module,f"Record successful")

        except Exception as e:
            log_system_error(module,f"Recording etl metadata failed")
            raise
        
    conn.close()