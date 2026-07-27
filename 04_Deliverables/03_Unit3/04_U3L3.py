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

def execute_query(query, mode, values=(), rows_list=[]):
    '''Establishes Connection with Database, executes Query and returns Result'''
    logging.info("Connecting to Database")
        
    mode = mode.strip().lower()
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=5432
        )
        logging.info("Connection Successful")
    except Exception as e: 
        logging.error(f"Connection failed: {e}")
        raise
    
    with conn.cursor() as cursor:
    
        logging.info(f"Executing Query | Mode: {mode} | {query}")
        
        try:
            if mode == 'execute_only':
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                return True
            elif mode == 'insert_rows':
                if not rows_list:
                    logging.warning("Rows insertion failed: Rows list empty")
                    conn.close()
                    return False
                for row in rows_list:
                    data = tuple(row.values())
                    cursor.execute(query,data)
                conn.commit()
                logging.info(f"Inserted {len(rows_list)} rows successfully")
                conn.close()
                return True
            elif mode == "fetch_one":
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Result: {result}")
                conn.close()
                return result
            elif mode == "fetch_all":
                cursor.execute(query, values)
                result = cursor.fetchall()
                logging.info(f"Result size: {len(result)} rows fetched")
                conn.close()
                return result
            else:
                logging.error(f"Invalid mode: {mode}")
                conn.close()
                raise ValueError(f"Invalid execution mode: {mode}")
            
        except Exception as e: 
            logging.error(f"Execution failed: {e}")
            conn.rollback()
            logging.info(f"Transaction rolled back")
            conn.close()
            raise
        
def main():
    # File Paths
    root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
    file_path = root_path + "01_Data/clean/dealer.csv"
    # Read file
    rows_list = read_csv(file_path)
    # Create table
    create_query = '''
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
    execute_query(query=create_query,mode='execute_only')
    # Insert rows
    insert_query = '''INSERT INTO clean_dealer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    execute_query(query=insert_query,mode='insert_rows',rows_list=rows_list)
    
if __name__=='__main__':
    main()