from config import reqd_fields_dict,id_fields_dict,int_fields,float_fields,date_fields,field_range_dict
from logger import log_info,log_data_error,log_system_error

from datetime import datetime

module = "[TRANSFORM]"

def normalize_null(value):
    '''Normalizes null values into None'''

    if isinstance(value,str):
        value = value.strip()
        if value.lower() in {'null','none','na','n/a',''}:
            return None
        
    return value

def normalize_null_row(row):
    '''Normalizes all null values into None in row and returns row'''

    for field in row:
        row[field] = normalize_null(row.get(field))

    return row

def check_reqd_fields(row,row_no,reqd_fields):
    '''Checks if required fields are present in the row'''

    try:
        missing_fields = [] 

        for field in reqd_fields:
            if not row.get(field):
                missing_fields.append(field)

    except (TypeError,ValueError) as e:
        log_data_error(module,f"Unexpected error during required fields check: {e}")

    if missing_fields:
        log_data_error(module,f"Row number = {row_no} | Missing required fields: {missing_fields}")
        return "E001_MISSING_REQUIRED"
    
    return None

def check_types(row,row_no):
    '''Checks data types (int, float and dates) are consistent'''

    bad_type_fields = []

    for field in int_fields:
        value = row.get(field)
        if value is not None:
            try:
                row[field] = int(value)

            except (TypeError,ValueError) as e:
                bad_type_fields.append(field)

    for field in float_fields:
        value = row.get(field)
        if value is not None:
            try:
                row[field] = float(value)

            except (TypeError,ValueError) as e:
                bad_type_fields.append(field)

    for field in date_fields:
        value = row.get(field)
        if value is not None:
            try:
                row[field] = datetime.strptime(value,"%Y-%m-%d")

            except (TypeError,ValueError) as e:
                bad_type_fields.append(field)     

    if bad_type_fields:
        log_data_error(module,f"Row number = {row_no} | Bad type fields: {bad_type_fields}")
        return row, "E002_BAD_TYPE"
    
    return row, None

def check_rule(value,condition,range):
    '''Checks if value satisfies condition and range'''

    if range is None:
        return True
    if condition == 'gt':
        return value > range
    if condition == 'gte':
        return value >= range
    if condition == 'lt':
        return value < range
    if condition == 'lte':
        return value <= range
    if condition == 'in':
        return value in range
    return False

def check_ranges(row,row_no):
    '''Checks data ranges as per business logic'''

    out_of_range_fields = []
    field_range_dict_fields = set(field_range_dict.keys())

    for field in row:
        try:    
            if field in field_range_dict_fields:
                value = row.get(field)
                rules = field_range_dict.get(field).copy()
                if value is not None:
                    for condition in rules:
                        range = rules.get(condition)
                        if not check_rule(value,condition,range):
                            out_of_range_fields.append(field)

        except (TypeError,ValueError) as e:
            log_data_error(module,f"Unexpected error during field range check: {e}")

    if out_of_range_fields:
        log_data_error(module,f"Row number = {row_no} | Out of range fields: {out_of_range_fields}")
        return "E003_OUT_OF_RANGE"
    
    return None

def get_field_values(file_name,row_list,field):
    '''Returns a set of unique field values'''
    log_info(module,f"Extracting values | File = {file_name.split('.')[0].split('_')[-1]} | Field = {field}")

    value_set = set()

    for row in row_list:
        value = eval(row.get(field))
        if value is not None:
            value_set.add(value)
    log_info(module,f"Found {len(value_set)} unique {field}(s)")

    return value_set

def check_fk_relation(row,row_no,id_sets):
    '''Checks foreign-key relationship with master table data provided as input in dictionary format (key->id_field,value->id_set)'''

    fk_violated_fields = []

    for id in id_sets:
        try:
            id_set = id_sets.get(id)
            id_value = row.get(id) 
            if not id_value in id_set:
                fk_violated_fields.append(id)

        except (TypeError,ValueError) as e:
            log_data_error(module,f"Unexpected error during FK violation check: {e}")

    if fk_violated_fields:
        log_data_error(module,f"Row number = {row_no} | FK violating fields: {fk_violated_fields}")
        return "E004_FK_VIOLATION"
    
    return None

def validate_row(file_name,row,row_no,id_sets=None):
    '''Performs required fields check, data types check, range check and FK violation check for row'''
    # log_info(module,f"Validating | Row number: {row_no}")

    file = file_name.split('.')[0].split('_')[-1]
    reqd_fields = reqd_fields_dict.get(file).copy()

    try:
        error = check_reqd_fields(row,row_no,reqd_fields)
        if error:
            return row, error
        
        val_row, error = check_types(row,row_no)
        if error:
            return val_row, error
        
        error = check_ranges(val_row,row_no)
        if error:
            return val_row, error
        
        if id_sets:
            error = check_fk_relation(val_row,row_no,id_sets)
            if error:
                return val_row, error
            
    except (TypeError,ValueError) as e:
        log_data_error(module,f"Unexpected error during data validation: {e}")

    return val_row, None

def validate_rows(file_name,row_list,id_sets=None):
    '''Normalizes and validates all rows and returns valid and invalid row sets'''
    log_info(module,f"Validating | {file_name}")

    file = file_name.split('.')[0].split('_')[-1]
    row_no = 0
    seen_ids = set()
    id_field = id_fields_dict.get(file)
    valid_rows = []
    invalid_rows = []
    error_counts = {
        "E001_MISSING_REQUIRED": 0,
        "E002_BAD_TYPE": 0,
        "E003_OUT_OF_RANGE": 0,
        "E004_FK_VIOLATION": 0,
        "E005_DUPLICATE_ID": 0
    }

    try: 
        for row in row_list:
            row_no += 1

            norm_row = normalize_null_row(row)
            val_row, error = validate_row(file_name,norm_row,row_no,id_sets)

            if not error:
                if val_row[id_field] in seen_ids:
                    error = "E005_DUPLICATE_ID"
                    log_data_error(f"Row number = {row_no} | Duplicate {id_field}")

            if error:
                val_row['error'] = error
                invalid_rows.append(val_row)
                error_counts[error] += 1
            else:
                valid_rows.append(val_row)
                seen_ids.add(val_row.get(id_field))

    except Exception as e:
        log_system_error(module,f"Unexpected Error: {e}")
        raise

    total_cnt = len(row_list)
    valid_cnt = len(valid_rows)
    invalid_cnt = len(invalid_rows)
    log_info(module,f"Validation Complete | Total rows = {total_cnt} | Valid rows = {valid_cnt} | Invalid rows = {invalid_cnt}")
    
    validation_summary = {
        'total_rows' : total_cnt,
        'valid_rows' : valid_cnt,
        'invalid_rows' : invalid_cnt,
        'error_count_by_type' : error_counts
    }

    return  valid_rows, invalid_rows, validation_summary
    