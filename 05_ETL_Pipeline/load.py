from config import DB_HOST,DB_NAME,DB_USER,DB_PORT
from config import field_names_dict, postgres_load_queries, batch_size_dict
from logger import log_info,log_warning,log_system_error

import os
from dotenv import load_dotenv
load_dotenv()

import csv
import psycopg2
from datetime import datetime

module = "[LOAD]"

def save_to_local(file_name,row_list,local_path):
    '''Takes list of row dictionaries and saves as csv file locally'''
    log_info(module,f"Saving {file_name} to local")
    if not row_list:
        log_warning(module,f"Provided row list is empty")
        return
    file = file_name.split('_')[-1]
    field_names = field_names_dict.get(file)
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

def get_db_connection():
    '''Returns Database connection object'''
    try:
        log_info(module,f"Connecting to database")
        conn = psycopg2.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = DB_USER,
            password = os.getenv("DB_PASS")
        )
        log_info(module,f"Connection successful")
        return conn
    except ConnectionError as e:
        log_system_error(module,f"Connection Failed: {e}")
        raise
    except Exception as e:
        log_system_error(module,f"Unexpected Error: {e}")   
        raise 


def load_to_database(file_name, row_list):
    '''Takes list of row dictionaries and loads into database'''
    log_info(module,f"Loading {file_name} to database")
    if not row_list:
        log_warning(module,f"Provided row list is empty")
        return
    file = file_name.split('_')[-1]
    field_names = field_names_dict.get(file)
    value_tuples_list = [(row.get(field) for field in field_names) for row in row_list]
    query = postgres_load_queries.get(file)
    total_cnt = len(row_list)
    batch_size = batch_size_dict.get(file)
    if not batch_size:
        batch_size = total_cnt   
    insert_cnt = 0
    conn = get_db_connection() 
    with conn.cursor() as cursor:
        for i in range(batch_size):
            batch_no = (i/batch_size) + 1
            try:
                log_info(module,f"Batch {batch_no} transaction begin")
                batch = value_tuples_list[i:i+batch_size]
                cursor.executemany(query,batch)
                conn.commit()
                log_info(module,f"Transaction successful | Inserted {len(batch)} row(s)")
                insert_cnt += len(batch)
            except Exception as e:
                log_warning(module,f"Transaction failed: {e}")
                conn.rollback()
                log_info(module,f"Transaction rolled back")
    conn.close()
    return {
        'job_name': file_name + " load",
        ''
    }

def record_load