import csv
import json
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


root_path = 'C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/'
product_file_path = root_path + '01_Data/dirty/product.csv'
dealer_file_path = root_path + '01_Data/dirty/dealer.csv'
inventory_file_path = root_path + '01_Data/dirty/inventory.csv'
clean_inventory_file_path = root_path + '04_Deliverables/02_Unit2/04_clean_inventory.csv'
reject_inventory_file_path = root_path + '04_Deliverables/02_Unit2/05_reject_inventory.csv'
summary_file_path = root_path + '04_Deliverables/02_Unit2/06_validation_summary.json'

def normalize_null(value):
    '''Normalizes null values for string columns'''
    if value is None or not isinstance(value,str):
        return value
    value = value.strip()
    if value.lower() in {"none","null","nan","na",""}:
        return None
    return value

def safe_int(value):
    '''Safely type casts into integers'''
    try:
        return int(normalize_null(value))
    except(TypeError,ValueError):
        return None

def safe_float(value):
    '''Safely type casts into floating numbers'''
    try:
        return float(normalize_null(value))
    except(TypeError,ValueError):
        return None

def get_null_normalized_row(row):
    '''Returns null normalized form of row'''
    for field in row:
        row[field] = normalize_null(row.get(field))
    return row

def load_csv(file_path):
    '''Loads csv files into list of null normalized row(s) in dictionary format'''
    file_list = []
    with open(file_path,newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_list.append(get_null_normalized_row(row))
    return file_list

def get_normalized_field_set(file_list,field):
    '''Returns a set of the field values (null normalized) from the file list'''
    field_set = set()
    for row in file_list:
        field_set.add(normalize_null(row.get(field)))
    return field_set

def validate_required_fields(row):
    '''Checks if required fields are present in row and returns errors'''
    required = ["inventory_id","dealer_id","product_id","on_hand_qty","on_order_qty","reorder_qty"]
    errors = []
    for field in required:
        if not row.get(field):
            errors.append(("E001",f"Missing {field}"))
    return errors

def validate_inventory_field_types(row):
    '''Validates quantity field type as int and date format and returns validated row and errors'''
    errors = []
    quantity_fields = ['on_hand_qty','on_order_qty','reorder_qty']
    for field in quantity_fields:
        row[field] = safe_int(row.get(field))
        if not row.get(field):
            errors.append(("E002",f"Invalid {field} type"))

    dates_fields = ['snapshot_date','last_restock_date','last_sale_date']
    for field in dates_fields:
        try:
            row[field] = datetime.strptime(row.get(field),'%Y-%m-%d')
        except(TypeError,ValueError):
            errors.append(("E003",f"Invalid {field} format"))

    return row, errors

def validate_quantity_range(row):
    '''Validates quantity range to be positive'''
    errors = []
    quantity_fields = ['on_hand_qty','on_order_qty','reorder_qty']
    for field in quantity_fields:
        quantity = row.get(field)
        if quantity and quantity < 0:
            errors.append(("E004",f"Negative {field}"))
    return errors

def validate_inventory_foreign_keys(row,product_id_set,dealer_id_set):
    '''Validates dealers and products from master tables'''
    errors = []
    product_id = row.get('product_id')
    dealer_id = row.get('dealer_id')
    if not product_id in product_id_set:
        errors.append(("E005","Invalid product_id"))
    if not dealer_id in dealer_id_set:
        errors.append(("E006","Invalid dealer_id"))
    return errors

def main(product_file_path,dealer_file_path,inventory_file_path,clean_inventory_file_path,reject_inventory_file_path,summary_file_path):
    '''Orchestrates the entire Ingestion, Validation and Output Process'''

    logging.info(f"File Loading | {product_file_path.split('/')[-1]}")
    product_file_list = load_csv(product_file_path)
    product_id_set = get_normalized_field_set(product_file_list,'product_id')
    logging.info(f"File Loading | {product_file_path.split('/')[-1]}")
    dealer_file_list = load_csv(dealer_file_path)
    dealer_id_set = get_normalized_field_set(dealer_file_list,'dealer_id')
    logging.info(f"File Loading | {inventory_file_path.split('/')[-1]}")
    inventory_file_list = load_csv(inventory_file_path)
    inventory_fields = list(inventory_file_list[0].keys())

    row_count = 0
    valid_row_count = 0
    invalid_row_count = 0
    error_summary = {
        "E001": {
            'desc': "Missing required Field",
            'count': 0
        },
        "E002": {
            'desc': "Invalid quantity type",
            'count': 0
        },
        "E003": {
            'desc': "Invalid date format",
            'count': 0
        },
        "E004": {
            'desc': "Negative Quantity",
            'count': 0
        },
        "E005": {
            'desc': "Invalid product_id",
            'count': 0
        },
        "E006": {
            'desc': "Invalid dealer_id",
            'count': 0
        }
    }

    with open(clean_inventory_file_path,mode="w",newline="") as f_clean, open(reject_inventory_file_path,mode="w",newline="") as f_reject, open(summary_file_path,mode="w") as f_summary:
        clean_writer = csv.DictWriter(f_clean,fieldnames=inventory_fields)
        clean_writer.writeheader()
        reject_writer = csv.DictWriter(f_reject,fieldnames=inventory_fields+['Error'])
        reject_writer.writeheader()

        for row in inventory_file_list:
            row_count += 1
            norm_row = get_null_normalized_row(row)
            logging.info(f"Validating | Inventory Row Count: {row_count}")
            errors = []

            temp_errors = validate_required_fields(norm_row)
            errors.extend(temp_errors)

            val_row, temp_errors = validate_inventory_field_types(norm_row)
            errors.extend(temp_errors)

            temp_errors = validate_quantity_range(val_row)
            errors.extend(temp_errors)

            temp_errors = validate_inventory_foreign_keys(val_row,product_id_set,dealer_id_set)
            errors.extend(temp_errors)

            if errors:
                invalid_row_count += 1
                logging.error(str(errors))
                val_row['Error'] = ""
                for code in set([error[0] for error in errors]):
                    val_row['Error'] += code + " "
                    error_summary[code]['count'] += 1
                reject_writer.writerow(row)
            else:
                valid_row_count += 1
                clean_writer.writerow(val_row)

        logging.info(f" Validation Complete | Valid rows: {valid_row_count} | Invalid rows: {invalid_row_count}")

        summary = {
            'total rows': row_count,
            'valid count': valid_row_count,
            'reject count': invalid_row_count,
            'error_summary': error_summary
        }   

        json.dump(summary, f_summary, indent=4) 

main(product_file_path,dealer_file_path,inventory_file_path,clean_inventory_file_path,reject_inventory_file_path,summary_file_path)

