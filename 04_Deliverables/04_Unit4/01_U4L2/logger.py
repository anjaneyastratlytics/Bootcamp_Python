from config import log_file_path

import logging
logging.basicConfig(
    filename = log_file_path,
    filemode = 'a',
    level = logging.INFO,
    format ="%(asctime)s %(levelname)s %(message)s"
)

def log_info(stage,msg):
    logging.info(stage+msg)

def log_warning(stage,msg):
    logging.warning(stage+msg)

def log_error(stage,msg):
    logging.error(stage+msg)