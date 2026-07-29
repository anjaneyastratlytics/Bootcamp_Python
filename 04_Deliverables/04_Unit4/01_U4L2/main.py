from config import bucket_name, input_object_key, input_local_path, output_clean_local_path, output_reject_local_path, output_clean_object_key,output_reject_object_key
from ingest import download_file, read_csv
from transform import get_normalized_rows, validate_rows, log_validation_summary
from load import save_files, upload_file



def main():
    '''Orchestrates the entire pipeline'''

    # Ingest
    ## Download file from AWS S3 bucket
    download_file(bucket_name,input_object_key,input_local_path)
    ## Read downloaded files
    row_list, field_names = read_csv(input_local_path)

    # Transform
    ## Normalize nulls in input
    norm_row_list = get_normalized_rows(row_list)
    ## Data validation and clean-reject segregation
    valid, invalid, error_summary = validate_rows(norm_row_list)
    ## Log validation summary
    log_validation_summary(len(valid),len(invalid),error_summary)

    # Load 
    ## Save transformed data to local
    save_files(valid, invalid, field_names, output_clean_local_path, output_reject_local_path)
    ## Upload processed files to AWS S3 bucket
    upload_file(output_clean_local_path,bucket_name,output_clean_object_key)
    upload_file(output_reject_local_path,bucket_name,output_reject_object_key)

if __name__=='__main__':
    main()