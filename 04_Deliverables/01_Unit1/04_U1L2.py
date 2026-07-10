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
    
with open(ip_dealer_file_path, newline="") as f_in, open(op_clean_file_path, mode="w", newline="") as f_clean, open(op_reject_file_path, mode="w", newline="") as f_reject:
    
    reader = csv.DictReader(f_in)
    clean_writer = csv.DictWriter(f_clean, fieldnames=reader.fieldnames)
    clean_writer.writeheader()
    reject_writer = csv.DictWriter(f_reject, fieldnames=reader.fieldnames+['error_code']) 
    reject_writer.writeheader()

    clean_count = 0
    reject_count = 0

    for row in reader:
        dealer_id = normalize_null(row.get("dealer_id",None))
        dealer_name = normalize_null(row.get("dealer_name",None))
        region = normalize_null(row.get("region",None)).upper()
        credit_term = normalize_null(row.get("credit_terms_days",None))

        dealer_info = ((str(dealer_id) + ' | ') if dealer_id else '') + (dealer_name if dealer_name else '')
        print(f"[INFO] Processing dealer {dealer_info}...")
        
        row["dealer_id"] = dealer_id
        row["dealer_name"] = dealer_name
        row["region"] = region
        row["credit_terms_days"] = credit_term
        
        if dealer_id is None:
            row['error_code'] = 'E001'
            reject_writer.writerow(row)
            reject_count+=1
            print(f"[Error E001]: Missing dealer_id")
        elif dealer_name is None:
            row['error_code'] = 'E002'
            reject_writer.writerow(row)
            reject_count+=1
            print(f"[Error E002]: Missing dealer_name")
        elif region not in {"NORTH", "SOUTH", "EAST", "WEST"}:
            row['error_code'] = 'E003'
            reject_writer.writerow(row)
            reject_count+=1
            print(f"[Error E003]: Invalid region")
        elif (credit_term is not None) and ( not str.isdigit(credit_term)):
            row['error_code'] = 'E004'
            reject_writer.writerow(row)
            reject_count+=1
            print(f"[Error E004]: Non-numeric credit terms value")
        else:
            clean_writer.writerow(row)
            clean_count+=1
            print(f"Dealer has a valid record.")
    
    print(f"Created Clean file with {clean_count} record(s) and reject file with {reject_count} record(s).")