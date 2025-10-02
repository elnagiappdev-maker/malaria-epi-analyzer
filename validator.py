# validator.py

def validate_record(record: dict) -> list:
    flags = []
    if not record.get("Patient Name / اسم المريض"):
        flags.append("Missing patient name")
    if not record.get("Species / نوع الطفيل"):
        flags.append("Missing species")
    return flags
