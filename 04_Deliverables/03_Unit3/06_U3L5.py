import csv
import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s %(levelname)s %(message)s"
)

def create_etl_audit_table():
    '''Creates etl audit table in Database'''

    try:
        logging.info("Connecting to Database...")
        conn =  psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        )
        logging.info("Connection Successful")
    except Exception as e: 
            logging.error(f"Connection failed: {e}")
            raise 
    
    with conn.cursor() as cursor:
        query = ''' 
            CREATE TABLE etl_audit(
                audit_id SERIAL PRIMARY KEY,
                job_name VARCHAR(100) NOT NULL,
                total_rows INTEGER NOT NULL,
                inserted_rows INTEGER NOT NULL,
                rejected_rows INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                run_timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        logging.info(f"Executing Query | {query}")
        try:
            cursor.execute(query)
            conn.commit()
            logging.info(f"Table created successfully")
        except Exception as e: 
            logging.error(f"Table creation failed: {e}")
            raise
        
    conn.close()

def create_clean_dealer_table():
    '''Creates clean dealer table in Database'''
    
    try:
        logging.info("Connecting to Database...")
        conn =  psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        )
        logging.info("Connection Successful")
    except Exception as e: 
            logging.error(f"Connection failed: {e}")
            raise 
    
    with conn.cursor() as cursor:
        query = '''
                CREATE TABLE clean_dealer(
                    dealer_id INT PRIMARY KEY,
                    dealer_code CHAR(10),
                    dealer_name VARCHAR(50),
                    city VARCHAR(30),
                    state CHAR(2),
                    region VARCHAR(5),
                    dealer_type VARCHAR(9),
                    created_date DATE,
                    is_active VARCHAR(5),
                    email TEXT,
                    phone TEXT,
                    credit_terms_days INT
                )'''
        logging.info(f"Executing Query | {query}")
        try:
            cursor.execute(query)
            conn.commit()
            logging.info(f"Table created successfully")
        except Exception as e: 
            logging.error(f"Table creation failed: {e}")
            raise
        
    conn.close()

def read_csv(file_path):
    '''Reads a csv file and returns a list of rows in dictionary format'''
    rows_list = []
    try:
        logging.info(f"Reading data from {file_path}")
        with open(file_path,newline="") as f: 
            reader = csv.DictReader(f)
            for row in reader:
                rows_list.append(row)
        logging.info(f"Successfully read {len(rows_list)} rows")
        return rows_list
    except Exception as e: 
        logging.error(f"Reading failed: {e}")
        raise
  
def insert_dealer_rows(query,rows_list=[]):
    '''Establishes Connection with Database, executes Query and returns Result'''
    
    logging.info("Connecting to Database")
    try:
        conn =  psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        ) 
        logging.info("Connection Successful")
    except Exception as e:
        logging.error(f"Connection failed: {e}")
        raise  
    
    summary = {
        "job_name": "dealer_load",
        "total_rows": len(rows_list),
        "inserted_rows": 0,
        "rejected_rows": 0,
        "status": "Success",
        "run_timestamp": datetime.now().isoformat()
    }

    with conn.cursor() as cursor:
        logging.info(f"Executing Query | {query}")

        if not rows_list:
            logging.warning(f"Rows insertion failed: Rows list empty")
            summary["status"] = "Failure"
            return summary
        
        insert_count = 0
        fail_count = 0

        for row in rows_list:
            try:
                cursor.execute(query,tuple(row.values()))
                insert_count += 1
            except Exception as e:
                fail_count += 1
                logging.warning(f"Failed to insert row: {e} | {row}")

        logging.info(f"Inserted {insert_count} rows")
        summary["inserted_rows"] = insert_count
        if fail_count > 0: 
            logging.error(f"Failed to insert {fail_count} rows")
            conn.rollback()
            logging.info(f"Transaction Rolled Back")
            summary["rejected_rows"] = fail_count
            summary["status"] = "Failure"
        else:
            conn.commit()

    conn.close() 
    return summary

def create_audit_record(summary,file_path):
    '''Creates record in audiit table in DB and returns summary as json file'''
    with open(file_path,"w") as f:
        json.dump(summary,f,indent=4)
    logging.info(f"Saved summary to {file_path}")

    logging.info("Connecting to Database")
    try:
        conn =  psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        ) 
        logging.info("Connection Successful")
    except Exception as e:
        logging.error(f"Connection failed: {e}")
        raise  
    
    summary_tuple = tuple(summary.values())
    query = '''INSERT INTO etl_audit(job_name,total_rows,inserted_rows,rejected_rows,status,run_timestamp)
            VALUES(%s,%s,%s,%s,%s,%s)'''

    with conn.cursor() as cursor:
        logging.info(f"Executing Query | {query}")
        
        try:
            cursor.execute(query,tuple(summary_tuple))
            conn.commit()
            logging.info(f"Created audit record")
        except Exception as e:
            logging.error(f"Failed to create audit record: {e}")
            conn.close()
            raise

    conn.close() 

def main():
    # File Paths
    root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"
    dealer_file_path = root_path + "01_Data/clean/dealer.csv"
    summary_file_path = root_path + "04_Deliverables/03_Unit3/07_dealer_load_summary.json"
    # Read file
    rows_list = read_csv(dealer_file_path)
    # Create table
    create_etl_audit_table()
    create_clean_dealer_table()
    # Insert rows
    insert_query = '''INSERT INTO clean_dealer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    summary = insert_dealer_rows(insert_query,rows_list)
    # Create audit record
    create_audit_record(summary,summary_file_path)
    
if __name__=='__main__':
    main()