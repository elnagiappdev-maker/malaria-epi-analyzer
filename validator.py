# validator.py

from typing import List, Dict

REQUIRED_FIELDS = [
    "Patient Name / اسم المريض",
    "Age / العمر",
    "Sex / الجنس",
    "Investigation Date / تاريخ التقصي",
    "Location / الموقع",
    "Investigator Name / اسم القائم بالتقصي",
]

def validate_record(record: Dict[str, str]) -> List[str]:
    """
    Validates a single patient record.
    Returns a list of error messages (if any).
    """
    errors = []

    for field in REQUIRED_FIELDS:
        value = record.get(field, "").strip()
        if not value:
            errors.append(f"Missing required field: {field}")

    return errors

def validate_records(records: List[Dict[str, str]]) -> Dict[int, List[str]]:
    """
    Validates multiple records.
    Returns a dict mapping record index to list of errors.
    """
    validation_results = {}
    for i, record in enumerate(records):
        errors = validate_record(record)
        if errors:
            validation_results[i] = errors
    return validation_results
