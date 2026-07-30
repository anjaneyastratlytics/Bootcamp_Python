from logger import log_info, log_warning, log_error

import json
from datetime import datetime

stage = "[Transform]"

def normalize_null(value):
    '''Normalizes null meaning value to standardized python None'''
    if value is None or not isinstance(value,str):
        return value
    value = value.strip()
    if value.lower() in {'none','null','nan','na','n/a',''}:
        return None
    return value

def get_normalized_rows(row_list):
    '''Returns entire row list after normalizing null for all fields of all rows'''
    log_info(stage,"Normalizing Null Values")
    for idx in range(len(row_list)):
        row = row_list[idx]
        for field in row:
            row_list[idx][field] = normalize_null(row.get(field))
    return row_list


def check_required_fields(row):
    '''Checks if the row contains all required fields'''
    required = ['dealer_id','dealer_code','dealer_name','region','dealer_type','created_date','is_active','credit_terms_days']
    errors = []
    for field in required:
        if not row.get(field):
            errors.append(("E001",f"Missing Required Field ({field})"))
    return errors

def validate_field_types_and_values(row):
    '''Checks specific field types, formats, and values as per predefined rules and returns validated row'''
    errors = []

    int_fields = ['dealer_id','credit_terms_days']
    for field in int_fields:
        if not row.get(field):
            continue
        try:
            row[field] = int(row.get(field))
        except(TypeError,ValueError):
            errors.append(("E002", f"Invalid {field} type"))

    date_fields = ['created_date']
    for field in date_fields:
        if not row.get(field):
            continue
        try:
            row[field] = datetime.strptime(row.get(field),'%Y-%m-%d')
        except(TypeError,ValueError):
            errors.append(("E003", f"Invalid {field} format"))

    valid_regions = {'NORTH','SOUTH','EAST','WEST'}
    region = row.get('region')
    if region:
        row[field] = region.upper()
    if region and region not in valid_regions:
        errors.append(("E004", f"Invalid {field} value"))    

    return row, errors

def validate_rows(row_list):
    '''Runs all predefined validations together'''
    error_summary = {
        "E001": {
            'description': "Missing Required Fields",
            'count': 0
        },
        "E002": {
            'description': "Invalid Integer Field(s) Type",
            'count': 0
        },
        "E003": {
            'description': "Invalid Date Field(s) Format",
            'count': 0
        },
        "E004": {
            'description': "Invalid Region Value",
            'count': 0
        }
    }
    valid = []
    invalid = []
    row_count = 0
    for row in row_list:
        row_count += 1
        log_info(stage,f"Validating row | Row Number: {row_count} | dealer_id: {row.get('dealer_id')}")
        errors = []

        mising_errors = check_required_fields(row)
        errors.extend(mising_errors)

        validated_row, val_errors = validate_field_types_and_values(row)
        errors.extend(val_errors)

        if errors:
            error_codes = set([e[0] for e in errors])
            error_descs = [e[1] for e in errors]
            log_warning(stage,f"Errors found: {error_descs}")
            for code in error_codes:
                error_summary[code]['count'] += 1
            validated_row['errors'] = error_descs
            invalid.append(validated_row)
        else:
            log_info(stage,f"No errors found")
            valid.append(validated_row)

    return valid, invalid, error_summary

def log_validation_summary(clean_cnt,reject_cnt,error_summary):
    '''Logs Validation Summary'''
    total_cnt = clean_cnt + reject_cnt
    clean_pct = round(100.0*clean_cnt/total_cnt,2)
    reject_pct = round(100.0*reject_cnt/total_cnt,2)
    log_info(stage,f"Validation Summary:\n1. Total rows processed = {total_cnt}\n2. Clean rows = {clean_cnt} ({clean_pct} %)\n3. Reject rows = {reject_cnt} ({reject_pct} %)\n4. Error Summary:\n{json.dumps(error_summary,indent=4)}")