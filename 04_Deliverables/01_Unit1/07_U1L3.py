import csv
import pprint
import json

# --------------------------------------------Paths----------------------------------------------

# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"

ip_product_file_path = root_path + "01_Data/dirty/product.csv"
ip_sales_log_file_path = root_path + "01_Data/dirty/sales_logs.jsonl"

# ------------------------------------------Functions--------------------------------------------

def normalize_null(value):
    if value is None:
        return None

    value = value.strip()
    
    if value.lower() in {"","na","null","nan"}:
        return None
    
    return value

def safe_int(value):
    try:
        return int(value)
    except(ValueError, TypeError):
        return None
    
def safe_float(value):
    try:
        return float(value)
    except(ValueError, TypeError):
        return None

def get_file_list(file_path):
    file_list = []
    with open(file_path) as f:
        r = csv.DictReader(f)
        for row in r:
            file_list.append(row)
    print(f"[INFO] Loaded {len(file_list)} records into list.")
    return file_list

def check_duplicates(file_list,field):
    seen = set()
    duplicates = []

    for row in file_list:
        id = row.get(field)
        if id in seen:
            duplicates.append(id)
        else:
            seen.add(id)

    print(f"[INFO] {len(duplicates)} duplicates found.")
    return duplicates

def product_count_by(file_list, field):
    cat_count = {}
    for row in file_list:
        cat = normalize_null(row.get(field))
        if cat in cat_count:
            cat_count[cat] += 1
        else:
            cat_count[cat] = 0

    print(f"[INFO] {len(cat_count)} unique categories found.")
    return cat_count

def get_sales_qty_by(sales_file_path, field):
    sales_qty_by_field = {}
    with open(sales_file_path) as sales:
        print("[INFO] Parsing sales jsonl file...")
        line_count = 0
        parse_count = 0
        for line in sales:
            line_count += 1

            try:
                record = json.loads(line)
                parse_count += 1

                event_id = normalize_null(record.get("event_id"))
                fld = record.get(field)
                qty = safe_int(record.get("qty"))

                if fld in sales_qty_by_field:
                    if qty:
                        sales_qty_by_field[fld] += qty
                    else:
                        print(f"[ERROR] Invalid Sales Qty for log event {event_id}")
                else:
                    sales_qty_by_field[fld] = 0

            except json.JSONDecodeError:
                print(f"[ERROR] Couldn't parse log line number {line_count}")
                continue
        print(f"[INFO] Total records: {line_count}, Records parsed successfully: {parse_count}")
    return sales_qty_by_field

# --------------------------------------------Main----------------------------------------------

product_list = get_file_list(ip_product_file_path)
duplicates_product_skus = check_duplicates(product_list,"sku")
print(duplicates_product_skus)
category_counts = product_count_by(product_list,"category")
print(category_counts)
sales_qty_by_product_id = get_sales_qty_by(ip_sales_log_file_path, "product_id")
print(sales_qty_by_product_id)