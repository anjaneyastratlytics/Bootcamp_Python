from logger import log_info

import time
from functools import wraps

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
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    backoff = delay * (2**attempt)
                    log_info(f"[SYSTEM] Waiting for {backoff}s before retrying")
                    time.sleep(backoff)
        return wrapper
    return decorator

def check_rule(value,condition,range):
    '''Checks if value satisfies condition and range'''
    if range is None:
        return True
    if condition == 'gt':
        return value > range
    if condition == 'gte':
        return value >= range
    if condition == 'lt':
            return value < range
    if condition == 'lte':
        return value <= range
    if condition == 'in':
        return value in range