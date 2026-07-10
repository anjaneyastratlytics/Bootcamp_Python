import csv
import pprint
import numpy as np
import pandas as pd

# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"

ip_dealer_file_path = root_path + "01_Data/dirty/dealer.csv"
op_clean_file_path = root_path + "04_Deliverables/01_Unit1/05_clean_dealer.csv"
op_reject_file_path = root_path + "04_Deliverables/01_Unit1/06_reject_dealer.csv"

def normalize_null(value):
    '''Normalizes Null and missing values to None type'''
    if value is None:
        return None

    value = value.strip()
    
    if value.lower() in {"","na","null","nan"}:
        return None
    
    return value

def safe_int(value):
    '''Safely type casts integer values'''
    try:
        return int(value)
    except(ValueError, TypeError):
        return None
    
def safe_float(value):
    '''Safely type casts float values'''
    try:
        return float(value)
    except(ValueError, TypeError):
        return None
    
def load_csv(file_path):
    '''Loads csv file as a list of dictionaries rows'''
    records = []
    with open(file_path, newline="") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            records.append(row)
    return records  

def clean_row(row):
    '''Cleans the row elements'''
    clean = row.copy()
    clean['dealer_id'] = safe_int(row.get('dealer_id'))
    clean['credit_terms_days'] = safe_int(row.get('credit_terms_days'))
    for col in row:
        val = row.get(col)
        if isinstance(val,str):
            val = normalize_null(val)
        clean[col]=val
    return clean

def validate_row(row):
    '''Validates cleaned rows based on specific rules'''
    errors = []

    dealer_id = row.get("dealer_id")
    dealer_code = row.get("dealer_code")
    dealer_name = row.get("dealer_name")
    region = row.get("region").upper()
    credit_term = row.get("credit_terms_days")
    dealer_info = str(dealer_id) if dealer_id else dealer_code

    print(f"[INFO] Processing dealer {dealer_info}...")

    if dealer_id is None:
        errors.append("[Error E001]: Missing dealer_id")
    elif dealer_name is None:
        errors.append("[Error E002]: Missing dealer_name")
    elif region not in {"NORTH", "SOUTH", "EAST", "WEST"}:
        errors.append("[Error E003]: Invalid region")
    elif (credit_term is not None) and ( not str.isdigit(credit_term)):
        errors.append("[Error E004]: Non-numeric credit terms value")

    return errors

def main():
    '''Orchestrates the entire loading, validating, segregating and error logging pipeline'''
    clean_records = []
    error_logs = []

    records = load_csv(ip_dealer_file_path)

    for row in records:
        cleaned_row = clean_row(row)
        errors = validate_row(cleaned_row)
        if errors:
            error_logs.append(
                {
                    'dealer_id': cleaned_row.get('dealer_id'),
                    'dealer_code': cleaned_row.get('dealer_code'),
                    'errors': errors
                 }
            )
        else:
            clean_records.append(cleaned_row)

    print(f"[INFO] Found {len(clean_records)} clean record(s) and {len(error_logs)} record(s) were rejected.")

    return clean_records, error_logs

clean_records, error_logs = main()

print("Clean records:\n\n")
for row in clean_records:
    pprint.pprint(row)
print("Error Logs:")
for log in error_logs:
    pprint.pprint(log)