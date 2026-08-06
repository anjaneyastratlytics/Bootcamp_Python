from logger import log_info, log_system_error

import time
from functools import wraps
from psycopg2 import DatabaseError
from botocore.exceptions import ClientError, ConnectTimeoutError, ReadTimeoutError, ConnectionError as BotoConnectionError

from dotenv import load_dotenv
load_dotenv()

def retry(max_attempts=3,delay=2):
    '''Returns retry decorator'''
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args,**kwargs)
                except (ConnectionError,TimeoutError,OSError,DatabaseError,ClientError,ConnectTimeoutError,ReadTimeoutError,BotoConnectionError) as e:
                    if attempt == max_attempts - 1:
                        raise
                    backoff = delay * (2**attempt)
                    log_info("[SYSTEM]",f"Waiting for {backoff}s before retrying")
                    time.sleep(backoff)
        return wrapper
    return decorator

