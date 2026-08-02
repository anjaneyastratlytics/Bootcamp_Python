from config import reqd_fields,int_fields,float_fields,date_fields,field_range_dict
from logger import log_info,log_data_error,log_system_error
from helper import check_rule

from datetime import datetime

module = "TRANSFORM"

def normalize_null(value):
    '''Normalizes null values into None'''
    if isinstance(value,str):
        value = value.strip().lower()
        if value in {'null','none','na','n/a',''}:
            return None
    return value

def normalize_null_row(row):
    '''Normalizes all null values into None in row and returns row'''
    for field in row:
        row[field] = normalize_null(row.get(field))
    return row

def check_reqd_fields(row):
    '''Checks if required fields are present in the row'''
    missing_fields = [] 
    for field in reqd_fields:
        if not row.get(field):
            missing_fields.append(field)
    if missing_fields:
        log_data_error(module,f"Missing required fields: {missing_fields}")
        return ["E001_MISSING_REQUIRED"]
    return []

def check_types(row):
    '''Checks data types (int, float and dates) are consistent'''
    bad_type_fields = []
    for field in int_fields:
        value = row.get(field)
        if value:
            try:
                value = int(value)
            except Exception as e:
                bad_type_fields.append(field)
    for field in float_fields:
            value = row.get(field)
            if value:
                try:
                    value = float(value)
                except Exception as e:
                    bad_type_fields.append(field)
    for field in date_fields:
            value = row.get(field)
            if value:
                try:
                    value = datetime.strptime(value,"%Y-%m-%d")
                except Exception as e:
                    bad_type_fields.append(field)     
    if bad_type_fields:
        log_data_error(module,f"Bad type fields: {bad_type_fields}")
        return ["E002_BAD_TYPE"]
    return []

def check_ranges(row):
    '''Checks data ranges as per business logic'''
    out_of_range_fields = []
    field_range_dict_fields = set(field_range_dict.keys())
    for field in row:
        if field in field_range_dict_fields:
            value = row.get(field)
            rules = field_range_dict.get(field)
            if value:
                for rule in rules:
                    if not check_rule(value,rule,rules.get(rule)):
                        out_of_range_fields.append(field)
    if out_of_range_fields:
        log_data_error(module,f"Out of range fields: {out_of_range_fields}")
        return ["E003_OUT_OF_RANGE"]
    return []

def check_fk_relation(row,id_sets):
    '''Checks foreign-key relationship with master table data provided as input in dictionary format (key->id_field,value->id_set)'''
    fk_violated_fields = []
    for id in id_sets:
        id_set = id_sets.get(id)
        id_value = row.get(id) 
        if not id_value in id_set:
            fk_violated_fields.append(id)
    if fk_violated_fields:
        log_data_error(module,f"FK violating fields: {fk_violated_fields}")
        return ["E004_FK_VIOLATION"]
    return []

def validate_row(row,row_no,id_sets):
    '''Performs required fields check, data types check, range check and FK violation check for row'''
    log_info(module,f"Validating | Row number: {row_no}")
    errors = []
    errors.append(check_reqd_fields(row))
    errors.append(check_types(row))
    errors.append(check_ranges(row))
    errors.append(check_fk_relation(row,id_sets))
    if errors:
        log_data_error(module,f"All errors found: {errors}")
        return errors
    return []

def validate_rows(file_name,row_list,id_sets,):
    '''Normalizes and validates all rows and returns valid and invalid row sets'''
    log_info(module,f"Validating | {file_name}")
    valid_rows = []
    invalid_rows = []
    row_no = 0
    error_counts = {
        "E001_MISSING_REQUIRED": 0,
        "E002_BAD_TYPE": 0,
        "E003_OUT_OF_RANGE": 0,
        "E004_FK_VIOLATION": 0
    }
    try:
        for row in row_list:
            row_no += 1
            norm_row = normalize_null(row)
            errors = validate_row(norm_row,row_no,id_sets)
            if errors:
                invalid_rows.append(norm_row)
                for error in errors:
                    error_counts[error] += 1
            else:
                valid_rows.append(norm_row)
        total_cnt = len(row_list)
        valid_cnt = len(valid_rows)
        invalid_cnt = len(invalid_rows)
        validation_summary = {
            'Total_Rows' : {total_cnt},
            'Valid_Rows' : {valid_cnt},
            'Invalid_Rows' : {invalid_cnt},
            'Error_Counts_By_Type' : {error_counts}
        }
        log_info(module,f"Validation Complete | Total rows = {total_cnt} | Valid rows = {valid_cnt} | Invalid rows = {invalid_cnt}")
        return  valid_rows, invalid_rows, validation_summary
    except Exception as e:
        log_system_error(module,f"Unexpected Error: {e}")
        raise