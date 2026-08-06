from config import raw_bucket,dirty_dealer_key,dirty_product_key,dirty_inventory_key,dirty_dealer_path,dirty_product_path,dirty_inventory_path
from config import clean_dealer_path,clean_product_path,clean_inventory_path,reject_dealer_path,reject_product_path,reject_inventory_path
from config import dealer_etl_summary_path, product_etl_summary_path, inventory_etl_summary_path
from logger import log_info
from helper import get_etl_status

from ingest import download_from_s3, generate_file_hash,get_rows_list_from_csv,is_already_processed
from transform import get_field_values,validate_rows
from load import save_to_local_csv, save_to_local_json, load_to_database, record_for_audit

import time
from datetime import datetime
    
def main():
    '''Orchestrates the entire ETL pipeline for dealer, product and inventory'''
    log_info("[MAIN]",f"\n\n{'*'*20}Pipeline Start{'*'*20}\n")

    # Dealer

    log_info("[MAIN]",f"\n{'-'*20}Dealer{'-'*20}")

    dealer_start_time = time.time()
    dealer_run_timestamp = datetime.now().isoformat()

    ## Ingest
    download_from_s3(raw_bucket,dirty_dealer_key,dirty_dealer_path)

    dirty_dealer_hash = generate_file_hash(dirty_dealer_path)
    dealer_processed = is_already_processed(dirty_dealer_hash)
    if not dealer_processed:

        dirty_dealer = get_rows_list_from_csv(dirty_dealer_path)

        dealer_ingest_time = time.time()
        dealer_ingest_duration = dealer_ingest_time-dealer_start_time

        ## Transform
        valid_dealer,invalid_dealer,dealer_validation_summary = validate_rows("dealer",dirty_dealer)

        dealer_transform_time = time.time()
        dealer_transform_duration = dealer_transform_time-dealer_ingest_time

        ## Load
        save_to_local_csv("valid_dealer",valid_dealer,clean_dealer_path)
        save_to_local_csv("invalid_dealer",invalid_dealer,reject_dealer_path)
        dealer_load_counts = load_to_database("valid_dealer",valid_dealer)

        dealer_load_time = time.time()
        dealer_load_duration = dealer_load_time-dealer_transform_time

        dealer_etl_summary = {
            'file_name': dirty_dealer_path.split('/')[-1],
            'file_hash': dirty_dealer_hash,
            'total_rows': dealer_validation_summary.get('total_rows'),
            'valid_rows': dealer_validation_summary.get('valid_rows'),
            'invalid_rows': dealer_validation_summary.get('invalid_rows'),
            'error_count_by_type': dealer_validation_summary.get('error_count_by_type'),
            'inserted_rows': dealer_load_counts.get('inserted_rows'),
            'failed_rows': dealer_load_counts.get('failed_rows'),
            'status': get_etl_status(dealer_validation_summary.get('total_rows'),dealer_validation_summary.get('valid_rows'),dealer_load_counts.get('inserted_rows')),
            'run_timestamp': dealer_run_timestamp,
            'execution_duration': f"{dealer_ingest_duration+dealer_transform_duration+dealer_load_duration:.2f} s"
        }

        record_for_audit(dealer_etl_summary)
        save_to_local_json("dealer_etl_summary",dealer_etl_summary,dealer_etl_summary_path)

        log_info("[MAIN]",f"""[TIMER] Dealer ETL execution time summary |
                  Ingest Duration = {dealer_ingest_duration:.2f} s
                  Transform Duration = {dealer_transform_duration:.2f} s
                  Load Duration = {dealer_load_duration:.2f} s""")

    # Product

    log_info("[MAIN]",f"\n{'-'*20}Product{'-'*20}")

    product_start_time = time.time()
    product_run_timestamp = datetime.now().isoformat()

    ## Ingest
    download_from_s3(raw_bucket,dirty_product_key,dirty_product_path)
    dirty_product_hash = generate_file_hash(dirty_product_path)
    product_processed = is_already_processed(dirty_product_hash)
    if not product_processed:
        dirty_product = get_rows_list_from_csv(dirty_product_path)

        product_ingest_time = time.time()
        product_ingest_duration = product_ingest_time-product_start_time

        ## Transform
        valid_product,invalid_product,product_validation_summary = validate_rows("product",dirty_product)

        product_transform_time = time.time()
        product_transform_duration = product_transform_time-product_ingest_time

        ## Load  
        save_to_local_csv("valid_product",valid_product,clean_product_path)
        save_to_local_csv("invalid_product",invalid_product,reject_product_path)
        product_load_counts = load_to_database("valid_product",valid_product)

        product_load_time = time.time()
        product_load_duration = product_load_time-product_transform_time

        product_etl_summary = {
            'file_name': dirty_product_path.split('/')[-1],
            'file_hash': dirty_product_hash,
            'total_rows': product_validation_summary.get('total_rows'),
            'valid_rows': product_validation_summary.get('valid_rows'),
            'invalid_rows': product_validation_summary.get('invalid_rows'),
            'error_count_by_type': product_validation_summary.get('error_count_by_type'),
            'inserted_rows': product_load_counts.get('inserted_rows'),
            'failed_rows': product_load_counts.get('failed_rows'),
            'status': get_etl_status(product_validation_summary.get('total_rows'),product_validation_summary.get('valid_rows'),product_load_counts.get('inserted_rows')),
            'run_timestamp': product_run_timestamp,
            'execution_duration': f"{product_ingest_duration+product_transform_duration+product_load_duration:.2f} s"
        }

        record_for_audit(product_etl_summary)
        save_to_local_json("product_etl_summary",product_etl_summary,product_etl_summary_path)

        log_info("[MAIN]",f"""[TIMER] product ETL execution time summary |
                  Ingest Duration = {product_ingest_duration:.2f} s
                  Transform Duration = {product_transform_duration:.2f} s
                  Load Duration = {product_load_duration:.2f} s""")

    # Inventory
    
    log_info("[MAIN]",f"\n{'-'*20}Inventory{'-'*20}")

    inventory_start_time = time.time()
    inventory_run_timestamp = datetime.now().isoformat()

    ## Ingest
    download_from_s3(raw_bucket,dirty_inventory_key,dirty_inventory_path)
    dirty_inventory_hash = generate_file_hash(dirty_inventory_path)
    if not is_already_processed(dirty_inventory_hash):
        dirty_inventory = get_rows_list_from_csv(dirty_inventory_path)

        inventory_ingest_time = time.time()
        inventory_ingest_duration = inventory_ingest_time-inventory_start_time

        ## Transform
        if dealer_processed:
            valid_dealer = get_rows_list_from_csv(clean_dealer_path)
        if product_processed:
            valid_product = get_rows_list_from_csv(clean_product_path)
        dealer_id_set = get_field_values("dealer.csv",valid_dealer,"dealer_id")
        product_id_set = get_field_values("product.csv",valid_product,"product_id")
        id_sets = {
            "dealer_id": dealer_id_set,
            "product_id": product_id_set
        }
        valid_inventory,invalid_inventory,inventory_validation_summary = validate_rows("inventory",dirty_inventory,id_sets)

        inventory_transform_time = time.time()
        inventory_transform_duration = inventory_transform_time-inventory_ingest_time

        ## Load
        save_to_local_csv("valid_inventory",valid_inventory,clean_inventory_path)
        save_to_local_csv("invalid_inventory",invalid_inventory,reject_inventory_path)
        inventory_load_counts = load_to_database("valid_inventory",valid_inventory)

        inventory_load_time = time.time()
        inventory_load_duration = inventory_load_time-inventory_transform_time

        inventory_etl_summary = {
            'file_name': dirty_inventory_path.split('/')[-1],
            'file_hash': dirty_inventory_hash,
            'total_rows': inventory_validation_summary.get('total_rows'),
            'valid_rows': inventory_validation_summary.get('valid_rows'),
            'invalid_rows': inventory_validation_summary.get('invalid_rows'),
            'error_count_by_type': inventory_validation_summary.get('error_count_by_type'),
            'inserted_rows': inventory_load_counts.get('inserted_rows'),
            'failed_rows': inventory_load_counts.get('failed_rows'),
            'status': get_etl_status(inventory_validation_summary.get('total_rows'),inventory_validation_summary.get('valid_rows'),inventory_load_counts.get('inserted_rows')),
            'run_timestamp': inventory_run_timestamp,
            'execution_duration': f"{inventory_ingest_duration+inventory_transform_duration+inventory_load_duration:.2f} s"
        }

        record_for_audit(inventory_etl_summary)
        save_to_local_json("inventory_etl_summary",inventory_etl_summary,inventory_etl_summary_path)

        log_info("[MAIN]",f"""[TIMER] inventory ETL execution time summary |
                  Ingest Duration = {inventory_ingest_duration:.2f} s
                  Transform Duration = {inventory_transform_duration:.2f} s
                  Load Duration = {inventory_load_duration:.2f} s""")
        
    log_info("[MAIN]",f"\n\n{'*'*20}Pipeline END{'*'*20}\n")


if __name__ == "__main__":
    main()