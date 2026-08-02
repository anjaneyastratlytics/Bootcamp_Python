from config import raw_bucket,dirty_dealer_key,dirty_product_key,dirty_inventory_key,dirty_dealer_path,dirty_product_path,dirty_inventory_path
from config import clean_dealer_path,clean_product_path,clean_inventory_path,reject_dealer_path,reject_product_path,reject_inventory_path,validation_summary_path
from logger import log_info

from ingest import download_from_s3, generate_file_hash,get_rows_list_from_csv,get_field_values,is_already_processed
from transform import validate_rows

def main():
    '''Orchestrates the entire ETL pipeline'''
    
    # Ingest
    ## S3 download
    download_from_s3(raw_bucket,dirty_dealer_key,dirty_dealer_path)
    download_from_s3(raw_bucket,dirty_product_key,dirty_product_path)
    download_from_s3(raw_bucket,dirty_inventory_key,dirty_inventory_path)
    ## Idempotency Guard
    dirty_dealer_hash = generate_file_hash(dirty_dealer_path)
    if is_already_processed(dirty_dealer_hash):
        return
    dirty_product_hash = generate_file_hash(dirty_product_path)
    if is_already_processed(dirty_product_hash):
        return
    dirty_inventory_hash = generate_file_hash(dirty_inventory_path)
    if is_already_processed(dirty_inventory_hash):
        return
    ## Read files
    dirty_dealer = get_rows_list_from_csv(dirty_dealer_path)
    dirty_product = get_rows_list_from_csv(dirty_product_path)
    dirty_inventory = get_rows_list_from_csv(dirty_inventory_path)
    
    #  Transform
    validation_summary = dict()
    ## Dealer 
    valid_dealer,invalid_dealer,dealer_validation_summary = validate_rows("dealer",dirty_dealer)
    validation_summary["dealer"] = dealer_validation_summary
    dealer_id_set = get_field_values("dealer.csv",valid_dealer,"dealer_id")
    ## Product
    valid_product,invalid_product,product_validation_summary = validate_rows("product",dirty_product)
    validation_summary["product"] = product_validation_summary
    product_id_set = get_field_values("product.csv",valid_product,"product_id")
    ## Inventory
    id_sets = {
        "dealer_id": dealer_id_set,
        "product_id": product_id_set
    }
    valid_inventory,invalid_inventory,inventory_validation_summary = validate_rows("inventory",dirty_inventory,id_sets)
    validation_summary["inventory"] = inventory_validation_summary
    
    # Load
    
if __name__ == "__main__":
    main()