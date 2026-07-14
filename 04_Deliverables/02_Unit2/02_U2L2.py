import csv
import logging

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)

# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"
inv_file_path = root_path + "01_Data/dirty/inventory.csv"
test_inv_file_path = root_path + "01_Data/dirty/test_inventory.csv"

def read_inventory(file_path):
    '''Generator-based file reader'''
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def validate_headers(row):
    '''Validates exact header matching for each row'''
    expected_headers = {"inventory_id","snapshot_date","dealer_id","product_id","on_hand_qty","on_order_qty","reorder_point","reorder_qty","last_restock_date","last_sale_date"}
    actual_headers = set(row.keys())
    return actual_headers == expected_headers

def main(file_path,limit=5):
    '''Orchestrates file read and validation upto a specified limit'''
    valid_row_count = 0
    row_count = 0
    logging.info(f"Ingestion started | {file_path.split('/')[-1]}")
    for row in read_inventory(file_path):
        if valid_row_count >= limit:
            break
        row_count += 1
        if validate_headers(row):
            valid_row_count += 1
            logging.info(f"Validated | inventory_id = {row.get('inventory_id')}")
        else:
            logging.error(f" Header mismatch | inventory_id = {row.get('inventory_id')}")
    logging.info(f"Validation Complete | Valid rows = {valid_row_count}, Invalid rows = {row_count-valid_row_count}")

# main(inv_file_path)
main(test_inv_file_path)