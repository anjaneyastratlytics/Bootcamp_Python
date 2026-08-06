# ETL Pipeline
---

This project consists of a complete production-ready ETL (Extract, Transform, and Load) Pipeline.

## Folder Structure

**Folder**,*File*

    **Root**
    |--*README.md*: You are **here**
    |--**Data**
    |   |--**Source**: Input files to work with
    |   |--**Processed**
    |   |   |--**Clean**: Processed files with only valid records
    |   |   |--**Reject**: Processed files with rejected records
    |   |--**Meta**: Summaries and log files
    |--*.env.example*: demo env file showing what data needs to be stored in original .env file before running the pipeline.
    |--*config.py*: Contains all configurable data, business rules and paths
    |--*logger.py*: Contains all logging formats and functions
    |--*helper.py*: Contains helper functions that don't belong to any specific stage in the pipeline
    |--*ingest.py*: Contains all data ingestion/extraction functions
    |--*transform.py*: Contains all transformation and validation functions 
    |--*load.py*: Contains all data loading functions
    |--*main.py*: Orchestrates the entire pipeline combining different modules together
    |--**tests**    
        |--*test_validation.py*: Unittest module for all pure transformation functions 

---

## Methodology

### Inputs

There are 3 input files:
- `dealer.csv`: dimension table consisting of dealer master data
- `product.csv`: dimension table consisting of product master data
- `inventory.csv`: facts table consisting of dealer-product combination inventory data snapshots

### Process

The pipeline follows the following process for each input file:
1. Downloads from AWS S3 bucket and saves locally.
2. Idempotency guard to check if it has already been processed using file content hashing and search in etl_audit table.
3. Performs the data transformations/validations.
    i. Required fields check
    ii. Field datatype check
    iii. Field range check
    iv. Foreign key violation check (only for inventory on dealer_id in dealer master and product_id on product master)
    v. Duplicacy check (primary key only)
4. Segregate records from source file into clean and reject files and save locally.
5. Load clean data to database (Postgres).
7. Output etl_summary (file_name,file_hash,total_rows,valid_rows,invalid_rows,inserted_rows,failed_rows,status,timestamps and execution durations) in json format and also load intop etl_audit table in database.

### Outputs / Results

- `clean_dealer.csv`
- `clean_product.csv`
- `clean_inventory.csv`
- `reject_dealer.csv`
- `reject_product.csv`
- `reject_inventory.csv`
- All clean files loaded into database
- 'dealer_etl_summary.json'
- 'product_etl_summary.json'
- 'inventory_etl_summary.json'
- 'pipeline.log'

---

## How to run?
Follow these steps to run this pipeline on your system:
1. First you need to have an AWS S3 bucket with all input files.
2. You also need to have a postgres server with all the tables required: dealer, product, inventory, and etl_audit. Refer `config.py` for attribute details.
3. Refer `.env.example` file and set up an actual .env file with the required data and credentials.
4. Refer `config.py` file for log formats, paths, pipeline configurations, and business rules.
5. Run the `main.py` file.
6. Run the `tests/test_validation.py` file to perform unit tests on pure validation functions