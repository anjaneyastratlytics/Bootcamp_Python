import csv
import pprint
import numpy as np
import pandas as pd

# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"

ip_dealer_file_path = root_path + "01_Data/dirty/dealer.csv"
op_clean_file_path = root_path + "04_Deliverables/01_Unit1/02_clean_dealer_preview.csv"
op_reject_file_path = root_path + "04_Deliverables/01_Unit1/03_reject_dealer_preview.csv"

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
    
dealer_text_fields = ['city','dealer_code','dealer_name','dealer_type','email','is_active','phone','region','state']

with open(ip_dealer_file_path, newline="") as f_in, open(op_clean_file_path, mode="w", newline="") as f_clean, open(op_reject_file_path, mode="w", newline="") as f_reject:
    
    reader = csv.DictReader(f_in)
    clean_writer = csv.DictWriter(f_clean, fieldnames=reader.fieldnames)
    clean_writer.writeheader()
    reject_writer = csv.DictWriter(f_reject, fieldnames=reader.fieldnames) 
    reject_writer.writeheader()
    
    clean_count = 0
    reject_count = 0
    
    for row in reader:
        dealer_id = normalize_null(row.get("dealer_id",None))
        if dealer_id:
            print(f"[INFO] Processing dealer {dealer_id}...")
        else:
            print(f"[INFO] Processing dealer without valid dealer_id...")
        
        dealer_name = normalize_null(row.get("dealer_name",None))
        row["dealer_name"] = dealer_name
        
        for col in dealer_text_fields:
            val = row.get(col,"")
            if val is not None:
                row[col] = val.strip()
                
        if dealer_name == None:
            reject_writer.writerow(row)
            print(f"[ERROR] Dealer has Invalid Name.")
            reject_count+=1
        else:
            clean_writer.writerow(row)
            print(f"[INFO] Dealer has Valid Name: {dealer_name}.")
            clean_count+=1
    
    print(f"Created Clean file with {clean_count} record(s) and reject file with {reject_count} record(s).")