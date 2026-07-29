# local file paths
root_path = '/home/name04/Desktop/Anjaneya/02_Bootcamp/04_Python/Bootcamp_Python/'
log_file_path = root_path + '04_Deliverables/04_Unit4/01_U4L2/01_pipeline.log'
input_local_path = root_path + '04_Deliverables/04_Unit4/01_U4L2/02_dirty_dealer.csv'
output_clean_local_path = root_path + '04_Deliverables/04_Unit4/01_U4L2/03_clean_dealer.csv'
output_reject_local_path = root_path + '04_Deliverables/04_Unit4/01_U4L2/04_reject_dealer.csv'

# AWS S3
bucket_name = 'raw-bucket-427763921511-ap-south-1-an'
input_object_key =  'dirty/dealer.csv'
output_clean_object_key = 'processed/clean/dealer.csv'
output_reject_object_key = 'processed/reject/dealer.csv'
