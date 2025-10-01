# validator.py

def validate_record(rec: dict) -> dict:
    """
    Return validation flags or errors for missing/invalid fields.
    """
    flags = {}
    required = ["patient_name", "patient_id"]
    for field in required:
        if not rec.get(field):
            flags[field] = "Missing"
        else:
            flags[field] = "OK"
    # Add more validation logic, for example:
    # if a date field is before another, or if numeric fields are in range
    return flags
