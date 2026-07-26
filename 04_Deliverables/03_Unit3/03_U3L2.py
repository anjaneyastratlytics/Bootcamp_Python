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
  
def execute_query(query,mode,values=(),rows_list=[]):
    '''Establishes Connection with Database, executes Query and returns Result'''
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
                logging.info(f"Executing Query | {query}")
                result = True
                try:
                    if mode.strip().lower() == 'execute_only':
                        cursor.execute(query,values)
                    elif mode.strip().lower() == 'insert_rows':
                        if not rows_list:
                            logging.warning(f"Rows insertion failed: Rows list empty")
                            return False
                        insert_count = 0
                        fail_count = 0
                        for row in rows_list:
                            try:
                                cursor.execute(query,tuple(row.values()))
                                insert_count += 1
                            except Exception as e:
                                fail_count += 1
                                logging.warning(f"Failed to insert row: {e} | {row}")
                        logging.info(f"Inserted {insert_count} rows successfully")
                        if fail_count > 0: 
                            logging.error(f"Failed to insert {fail_count} rows")
                            conn.rollback()
                            logging.info(f"Transaction Rolled Back")
                            raise
                    elif mode.strip().lower() == "one":
                        cursor.execute(query,values)
                        result = cursor.fetchone()
                        logging.info(f"Result:\n{result}")
                    elif mode.strip().lower() == "all":
                        cursor.execute(query,values)
                        result = cursor.fetchall()
                        logging.info(f"Result:\n{result}")
                    else:
                        logging.error(f"Invalid mode: {mode} | Valid mode examples: ['execute_only','insert_rows','fetch_one','fetchall',...]")
                        raise
                    logging.info(f"Query Execution Successful")
                    conn.commit()
                    logging.info(f"Transaction Committed")
                    return result
                except Exception as e: 
                    logging.error(f"Execution failed: {e}")
                    conn.rollback()
                    logging.info(f"Transaction Rolled Back")
                    raise
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