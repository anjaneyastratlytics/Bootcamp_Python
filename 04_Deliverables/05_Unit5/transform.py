def check_required(row):
    required_fields = ["dealer_id","dealer_code","region","credit_terms_days"]
    errors = []
    for field in required_fields:
        if not row.get(field):
            errors.append(f" Missing {field}")
        continue
    return errors

def check_range(row):
    if row.get("credit_terms_days") < 0:
        return ["Negative Credit Term"]
    return []

import hashlib
def generate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path,"rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()