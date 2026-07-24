import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s %(levelname)s %(message)s"
)

def execute_query(query,fetch=None):
    '''Estaablishes Connection with Database, executes Query and returns Result'''
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
                cursor.execute(query)
                if not fetch:
                    logging.info(f"Query Execution Successful")
                elif fetch.strip().lower() == "one":
                    result = cursor.fetchone()
                    logging.info(f"Result:\n{result}")
                elif fetch.strip().lower() == "all":
                    result = cursor.fetchall()
                    logging.info(f"Result:\n{result}")
                else:
                    logging.error(f"Invalid fetch mode: {fetch} | Valid fetch modes: ['one','all',None]")
    except Exception as e:
        logging.error(e)
    
def main():
    query = "SELECT 1;"
    execute_query(query,"one")
    return

if __name__=='__main__':
    main()