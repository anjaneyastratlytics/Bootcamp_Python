from config import raw_bucket,dirty_dealer_key,dirty_product_key,dirty_inventory_key,dirty_dealer_path,dirty_product_path,dirty_inventory_path
from config import clean_dealer_path,clean_product_path,clean_inventory_path,reject_dealer_path,reject_product_path,reject_inventory_path,validation_summary_path
from logger import log_info

from ingest import download_from_s3, generate_file_hash,get_rows_list_from_csv,is_already_processed
from transform import get_field_values,validate_rows

import time
    
def main():
    '''Orchestrates the entire ETL pipeline for dealer, product and inventory'''
    pipeline_start_time = time.time()
    log_info("[MAIN]",f"\n{'*'*20}Pipeline Start{'*'*20}\n\n")
    validation_summary = dict()

    # Dealer
    ## Ingest
    log_info("[MAIN]",f"\n{'-'*20}Dealer{'-'*20}")
    download_from_s3(raw_bucket,dirty_dealer_key,dirty_dealer_path)
    dirty_dealer_hash = generate_file_hash(dirty_dealer_path)
    if not is_already_processed(dirty_dealer_hash):
        dirty_dealer = get_rows_list_from_csv(dirty_dealer_path)
        dealer_ingest_time = time.time()
        log_info("[MAIN]",f"[TIMER] Dealer ingestion over in {dealer_ingest_time-pipeline_start_time:.2f} s")
        ## Transform
        valid_dealer,invalid_dealer,dealer_validation_summary = validate_rows("dealer",dirty_dealer)
        validation_summary["dealer"] = dealer_validation_summary
        dealer_transform_time = time.time()
        log_info("[MAIN]",f"[TIMER] Dealer transformation over in {dealer_transform_time-dealer_ingest_time:.2f} s")
        ## Load
        dealer_load_time = time.time()
        log_info("[MAIN]",f"[TIMER] Dealer load over in {dealer_load_time-dealer_transform_time:.2f} s")
    else:
        valid_dealer = get_rows_list_from_csv(dirty_dealer_path) # Replace dirty_dealer_path by valid_dealer_path that is already processed

    # Product
    ## Ingest
    log_info("[MAIN]",f"\n{'-'*20}Product{'-'*20}")
    download_from_s3(raw_bucket,dirty_product_key,dirty_product_path)
    dirty_product_hash = generate_file_hash(dirty_product_path)
    if not is_already_processed(dirty_product_hash):
        dirty_product = get_rows_list_from_csv(dirty_product_path)
        product_ingest_time = time.time()
        log_info("[MAIN]",f"[TIMER] Product ingestion over in {product_ingest_time-dealer_load_time:.2f} s")
        ## Transform
        valid_product,invalid_product,product_validation_summary = validate_rows("product",dirty_product)
        validation_summary["product"] = product_validation_summary    
        product_transform_time = time.time()
        log_info("[MAIN]",f"[TIMER] Product transformation over in {product_transform_time-product_ingest_time:.2f} s")
        ## Load  
        product_load_time = time.time()
        log_info("[MAIN]",f"[TIMER] Product load over in {product_load_time-product_transform_time:.2f} s")
    else:
        valid_product = get_rows_list_from_csv(dirty_product_path) # Replace dirty_product_path by valid_product_path that is already processed

    # Inventory
    ## Ingest
    log_info("[MAIN]",f"\n{'-'*20}Inventory{'-'*20}")
    download_from_s3(raw_bucket,dirty_inventory_key,dirty_inventory_path)
    dirty_inventory_hash = generate_file_hash(dirty_inventory_path)
    if not is_already_processed(dirty_inventory_hash):
        dirty_inventory = get_rows_list_from_csv(dirty_inventory_path)
        inventory_ingest_time = time.time()
        log_info("[MAIN]",f"[TIMER] Inventory ingestion over in {inventory_ingest_time-product_load_time:.2f} s")
        ## Transform
        dealer_id_set = get_field_values("dealer.csv",valid_dealer,"dealer_id")
        product_id_set = get_field_values("product.csv",valid_product,"product_id")
        id_sets = {
            "dealer_id": dealer_id_set,
            "product_id": product_id_set
        }
        valid_inventory,invalid_inventory,inventory_validation_summary = validate_rows("inventory",dirty_inventory,id_sets)
        validation_summary["inventory"] = inventory_validation_summary
        inventory_transform_time = time.time()
        log_info("[MAIN]",f"[TIMER] Inventory transformation over in {inventory_transform_time-inventory_ingest_time:.2f} s")
        ## Load
        inventory_load_time = time.time()
        log_info("[MAIN]",f"[TIMER] Inventory load over in {inventory_load_time-inventory_transform_time:.2f} s")


if __name__ == "__main__":
    main()