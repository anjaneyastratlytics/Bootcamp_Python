from config import log_format,pipeline_log_path
import logging

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    filename=pipeline_log_path,
    filemode="a"
)

def log_info(module,msg):
    logging.info(module+" "+msg)
    
def log_warning(module,msg):
    logging.warning(module+" "+msg)

def log_error(module,msg):
    logging.error(module+" "+msg)
    
def log_data_error(module,msg):
    logging.warning(module+" [DATA ERROR] "+msg)
    
def log_system_error(module,msg):
    logging.error(module+" [SYSTEM ERROR] "+msg)