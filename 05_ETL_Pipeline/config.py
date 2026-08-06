import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Logging Format
log_format = "%(asctime)s %(levelname)s %(message)s"

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
## S3
s3_region = os.getenv("S3_REGION")
raw_bucket = os.getenv("RAW_BUCKET")
dirty_dealer_key = os.getenv("DIRTY_DEALER_KEY")
dirty_product_key = os.getenv("DIRTY_PRODUCT_KEY")
dirty_inventory_key = os.getenv("DIRTY_INVENTORY_KEY")
dirty_sales_key = os.getenv("DIRTY_SALES_KEY")

# Postgres Connection
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PORT = os.getenv("DB_PORT")
DB_PASS = os.getenv("DB_PASS")

# Local Paths

root_path = Path(__file__).resolve().parent

pipeline_log_path = os.path.join(root_path,"Data/Meta/pipeline.log")

dirty_dealer_path = os.path.join(root_path,"Data/Source/dealer.csv")
dirty_product_path = os.path.join(root_path,"Data/Source/product.csv")
dirty_inventory_path = os.path.join(root_path,"Data/Source/inventory.csv")
dirty_sales_path =  os.path.join(root_path,"Data/Source/sales_logs.jsonl")

clean_dealer_path = os.path.join(root_path,"Data/Processed/Clean/dealer.csv")
clean_product_path = os.path.join(root_path,"Data/Processed/Clean/product.csv")
clean_inventory_path = os.path.join(root_path,"Data/Processed/Clean/inventory.csv")

reject_dealer_path = os.path.join(root_path,"Data/Processed/Reject/dealer.csv")
reject_product_path = os.path.join(root_path,"Data/Processed/Reject/product.csv")
reject_inventory_path = os.path.join(root_path,"Data/Processed/Reject/inventory.csv")

dealer_etl_summary_path = os.path.join(root_path,"Data/Meta/dealer_etl_summary.json")
product_etl_summary_path = os.path.join(root_path,"Data/Meta/product_etl_summary.json")
inventory_etl_summary_path = os.path.join(root_path,"Data/Meta/inventory_etl_summary.json")


# Data Validation
reqd_fields_dict = {
    "dealer": ['dealer_id','dealer_code','dealer_name','region','dealer_type','is_active','credit_terms_days'],
    "product": ['product_id','sku','product_name','category','unit_cost','unit_price','is_discontinued'],
    "inventory": ['inventory_id','snapshot_date','dealer_id','product_id','on_hand_qty','on_order_qty'],
    "sales": []
}

int_fields = ['dealer_id','credit_terms_days','product_id','dealer_id','product_id','on_hand_qty','on_order_qty','reorder_point','reorder_qty']
date_fields = ['created_date','snapshot_date','last_restock_date','last_sale_date']
float_fields = ['unit_cost','unit_price','weight_kg']
id_fields_dict = {
    "dealer": "dealer_id",
    "product": "product_id",
    "inventory": "inventory_id"
}

field_range_dict = {
    'unit_cost': {'gt':0,'gte':None,'lt':None,'lte':None,'in':None},
    'unit_price': {'gt':0,'gte':None,'lt':None,'lte':None,'in':None},
    'on_hand_qty': {'gt':None,'gte':0,'lt':None,'lte':None,'in':None},
    'on_order_qty': {'gt':None,'gte':0,'lt':None,'lte':None,'in':None},
    'reorder_qty': {'gt':None,'gte':0,'lt':None,'lte':None,'in':None}
}

# Load
field_names_dict = {
    "dealer": ['dealer_id','dealer_code','dealer_name','city','state','region','dealer_type','created_date','is_active','email','phone','credit_terms_days'],
    "product": ['product_id','sku','product_name','category','subcategory','brand','uom','unit_cost','unit_price','weight_kg','is_discontinued','created_date'],
    "inventory": ['inventory_id','snapshot_date','dealer_id','product_id','on_hand_qty','on_order_qty','reorder_point','reorder_qty','last_restock_date','last_sale_date'],
    "etl_audit": ['file_name','file_hash','total_rows','valid_rows','invalid_rows','inserted_rows','failed_rows','status','run_timestamp']
}
postgres_load_queries = {
    "dealer": '''INSERT INTO dealer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    "product": '''INSERT INTO product VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    "inventory": '''INSERT INTO inventory VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    "etl_audit": '''INSERT INTO etl_audit(file_name,file_hash,total_rows,valid_rows,invalid_rows,inserted_rows,failed_rows,status,run_timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
}
batch_size_dict = {
    "dealer": None,
    "product": None,
    "inventory": 200
}