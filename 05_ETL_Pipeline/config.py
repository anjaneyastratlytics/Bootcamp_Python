# Logging Format
log_format = "%(asctime)s %(levelname)s %(message)s"

# AWS S3
s3_region = 'ap-south-1'
raw_bucket = 'raw-bucket-427763921511-ap-south-1-an'
dirty_dealer_key = 'dirty/dealer.csv'
dirty_product_key = 'dirty/product.csv'
dirty_inventory_key = 'dirty/inventory.csv'
dirty_sales_key = 'dirty/sales_logs.jsonl'

# PGADMIN DB
DB_HOST = "localhost"
# DB_NAME = "BootcampSL"
DB_NAME = "bootcamp"
DB_USER = "postgres"
DB_PORT = 5432

# Local Paths
# root_path = "C:/Users/KIIT/Desktop/Stratlytics/02_Bootcamp/04_Python/"
root_path = "/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/"

dirty_dealer_path = root_path + "05_ETL_Pipeline/Data/Source/dealer.csv"
dirty_product_path = root_path + "05_ETL_Pipeline/Data/Source/product.csv"
dirty_inventory_path = root_path + "05_ETL_Pipeline/Data/Source/inventory.cv"
dirty_sales_path = root_path + "05_ETL_Pipeline/Data/Source/sales_logs.jsonl"

pipeline_log_path = root_path + "05_ETL_Pipeline/Data/Meta/pipeline.log"

clean_dealer_path = root_path + "05_ETL_Pipeline/Data/Processed/Clean/dealer.csv"
clean_product_path = root_path + "05_ETL_Pipeline/Data/Processed/Clean/product.csv"
clean_inventory_path = root_path + "05_ETL_Pipeline/Data/Processed/Clean/inventory.cv"

reject_dealer_path = root_path + "05_ETL_Pipeline/Data/Processed/Reject/dealer.csv"
reject_product_path = root_path + "05_ETL_Pipeline/Data/Processed/Reject/product.csv"
reject_inventory_path = root_path + "05_ETL_Pipeline/Data/Processed/Reject/inventory.cv"

validation_summary_path = root_path + "05_ETL_Pipeline/Data/validation_summary.json"


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
    "inventory": ['inventory_id','snapshot_date','dealer_id','product_id','on_hand_qty','on_order_qty','reorder_point','reorder_qty','last_restock_date','last_sale_date']
}
postgres_load_queries = {
    "dealer": '''INSERT INTO dealer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    "product": '''INSERT INTO product VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    "inventory": '''INSERT INTO inventory VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
}
batch_size_dict = {
    "dealer": None,
    "product": None,
    "inventory": 200
}