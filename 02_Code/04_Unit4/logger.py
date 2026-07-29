from config import log_file_path

import logging
logging.basicConfig(
    filename = log_file_path,
    filemode = 'a',
    level = logging.INFO,
    format ="%(asctime)s %(levelname)s %(message)s"
)

def log_info(msg):
    logging.info(msg)

def log_warning(msg):
    logging.warning(msg)

def log_error(msg):
    logging.error(msg)