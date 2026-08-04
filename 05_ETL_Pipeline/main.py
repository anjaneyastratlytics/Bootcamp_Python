from config import raw_bucket,dirty_dealer_key,dirty_product_key,dirty_inventory_key,dirty_dealer_path,dirty_product_path,dirty_inventory_path
from config import clean_dealer_path,clean_product_path,clean_inventory_path,reject_dealer_path,reject_product_path,reject_inventory_path
from config import dealer_validation_summary_path, product_validation_summary_path, inventory_validation_summary_path
from logger import log_info

from ingest import download_from_s3, generate_file_hash,get_rows_list_from_csv,is_already_processed
from transform import get_field_values,validate_rows
from load import save_to_local, save_validation_summary, load_to_database, record_for_audit

import time
from datetime import datetime
    
def main():
    '''Orchestrates the entire ETL pipeline for dealer, product and inventory'''
    log_info("[MAIN]",f"\n{'*'*20}Pipeline Start{'*'*20}\n\n")

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
        save_to_local("valid_dealer",valid_dealer,clean_dealer_path)
        save_to_local("invalid_dealer",invalid_dealer,reject_dealer_path)
        save_validation_summary("dealer",dealer_validation_summary,dealer_validation_summary_path)
        dealer_load_counts = load_to_database("valid_dealer",valid_dealer)
        record_for_audit({
            'file_name': dirty_dealer_path.split('/')[-1],
            'file_hash': dirty_dealer_hash,
            'total_rows': len(dirty_dealer),
            'valid_rows': len(valid_dealer),
            'invalid_rows': len(invalid_dealer),
            'inserted_rows': dealer_load_counts.get('inserted_rows'),
            'failed_rows': dealer_load_counts.get('failed_rows'),
            'run_timestamp': dealer_run_timestamp
        })

        dealer_load_time = time.time()
        dealer_load_duration = dealer_load_time-dealer_transform_time

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
        save_to_local("valid_product",valid_product,clean_product_path)
        save_to_local("invalid_product",invalid_product,reject_product_path)
        save_validation_summary("product",product_validation_summary,product_validation_summary_path)
        product_load_counts = load_to_database("valid_product",valid_product)
        record_for_audit({
            'file_name': dirty_product_path.split('/')[-1],
            'file_hash': dirty_product_hash,
            'total_rows': len(dirty_product),
            'valid_rows': len(valid_product),
            'invalid_rows': len(invalid_product),
            'inserted_rows': product_load_counts.get('inserted_rows'),
            'failed_rows': product_load_counts.get('failed_rows'),
            'run_timestamp': product_run_timestamp
        })

        product_load_time = time.time()
        product_load_duration = product_load_time-product_transform_time

        log_info("[MAIN]",f"""[TIMER] Product ETL execution time summary |
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
        save_to_local("valid_inventory",valid_inventory,clean_inventory_path)
        save_to_local("invalid_inventory",invalid_inventory,reject_inventory_path)
        save_validation_summary("inventory",inventory_validation_summary,inventory_validation_summary_path)
        inventory_load_counts = load_to_database("valid_inventory",valid_inventory)
        record_for_audit({
            'file_name': dirty_inventory_path.split('/')[-1],
            'file_hash': dirty_inventory_hash,
            'total_rows': len(dirty_inventory),
            'valid_rows': len(valid_inventory),
            'invalid_rows': len(invalid_inventory),
            'inserted_rows': inventory_load_counts.get('inserted_rows'),
            'failed_rows': inventory_load_counts.get('failed_rows'),
            'run_timestamp': inventory_run_timestamp
        })

        inventory_load_time = time.time()
        inventory_load_duration = inventory_load_time-inventory_transform_time

        log_info("[MAIN]",f"""[TIMER] Inventory ETL execution time summary |
                  Ingest Duration = {inventory_ingest_duration:.2f} s
                  Transform Duration = {inventory_transform_duration:.2f} s
                  Load Duration = {inventory_load_duration:.2f} s""")


if __name__ == "__main__":
    main()