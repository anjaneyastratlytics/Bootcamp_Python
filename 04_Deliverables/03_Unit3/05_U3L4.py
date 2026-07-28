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

def create_clean_product_table():
    '''Creates clean product table in Database'''
    
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
            CREATE TABLE clean_product(
                product_id INT PRIMARY KEY,
                sku CHAR(12),
                product_name VARCHAR(50),
                category VARCHAR(30),
                subcategory VARCHAR(30),
                brand VARCHAR(30),
                uom VARCHAR(3),
                unit_cost NUMERIC(10, 2),
                unit_price NUMERIC(10, 2),
                weight_kg  NUMERIC(10, 2),
                is_discontinued VARCHAR(5),
                created_date DATE
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
    
def insert_rows_in_batches(query,rows_list,batch_size=200):
    '''Inserts rows into DB in batches'''
    
    try:
        logging.info("Connecting to Database...")
        conn = psycopg2.connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            port = 5432
        )
        logging.info("Connection Successful")
    except Exception as e: 
        logging.error(f"Failed to connect: {e}")
        raise
    
    logging.info(f"Initiating Batch Insertion | Rows = {len(rows_list)} | Batch Size = {batch_size} | Query = {query}")
    
    with conn.cursor() as cursor:
        values_tuple_list = [tuple(row.values()) for row in rows_list]
        insert_row_count = 0
        failed_row_count = 0
        failed_batches = []
        for i in range(0,len(values_tuple_list),batch_size):
            batch = values_tuple_list[i:i+batch_size]
            batch_no = i/batch_size + 1
            try:
                cursor.executemany(query,batch)
                conn.commit()
                insert_row_count += len(batch)
                logging.info(f"Batch {batch_no}: Inserted {len(batch)} rows.")
            except Exception as e:
                logging.warning(f"Batch {batch_no} failed: {e}")
                failed_batches.append(batch_no)
                failed_row_count += len(batch)
                conn.rollback()
                logging.info(f"Transaction Rolled Back")
                
        logging.info("All batches complete")
        logging.info(f"Inserted {insert_row_count} rows successfully")
        if failed_row_count > 0:
            logging.info(f"Failed {len(failed_batches)} batches consisting {failed_row_count} rows")
            logging.info(f"Failed batches: {failed_batches}")
    
    conn.close()

def main():
    # File Paths
    root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
    file_path = root_path + "01_Data/clean/product.csv"
    # Read file
    rows_list = read_csv(file_path)
    # Create table
    create_clean_product_table()
    # Insert rows
    insert_query = '''INSERT INTO clean_product VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    insert_rows_in_batches(query=insert_query,rows_list=rows_list)
    
if __name__=='__main__':
    main()