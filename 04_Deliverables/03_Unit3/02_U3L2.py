import csv
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s %(levelname)s %(message)s"
)

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
    
def create_clean_dealer_table():
    '''Creates clean dealer table in Database'''
    logging.info("Connecting to Database")
    try:
        with psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        ) as conn:
            logging.info("Connection Successful")
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
                        )
                    '''
                logging.info(f"Executing Query | {query}")
                try:
                    cursor.execute(query)
                    logging.info(f"Table created successfully")
                except Exception as e: 
                    logging.error(f"Table creation failed: {e}")
                    raise
    except Exception as e: 
        logging.error(f"Connection failed: {e}")
        raise 
    
def insert_rows_into_clean_dealer_table(rows_list):
    '''Inserts rows into clean dealer table'''
    logging.info("Connecting to Database")
    try:
        with psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        ) as conn:
            logging.info("Connection Successful")
            with conn.cursor() as cursor:
                logging.info(f"Executing Table Population Query")
                insert_count = 0
                for row in rows_list:
                    try:
                        cursor.execute('''
                            INSERT INTO clean_dealer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ''',tuple(row.values()))
                        insert_count += 1
                    except Exception as e:
                        logging.warning(f"Row insertion failed: {e} | {row}")
                insert_pct = round(100.0*insert_count/len(rows_list),2)
                logging.info(f"{insert_count} rows inserted successfully ({insert_pct} % of total)")
                failed_count = len(rows_list)-insert_count
                if failed_count > 0:
                    failed_pct = round(100.0*failed_count/len(rows_list),2)
                    logging.info(f"Failed to insert {len(rows_list)-insert_count} rows ({failed_pct} % of total)")
    except Exception as e: 
        logging.error(f"Connection failed: {e}") 
        raise
        
def main():
    # File Paths
    root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
    file_path = root_path + "01_Data/clean/dealer.csv"
    # Read file
    rows_list = read_csv(file_path)
    # Create table
    create_clean_dealer_table()
    # Insert rows
    insert_rows_into_clean_dealer_table(rows_list)
    
if __name__=='__main__':
    main()