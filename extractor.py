# extractor.py

import re

def extract_fields_from_text(text: str) -> dict:
    """
    Extract fields from the raw OCR text.
    You’ll need to adjust regex or parsing logic based on your form layout.
    """
    rec = {}
    # Example: find “Patient Name: <value>” in text (adjust to your actual form)
    m = re.search(r"Patient Name[:\s]+([A-Za-z0-9 ]+)", text)
    if m:
        rec["patient_name"] = m.group(1).strip()
    else:
        rec["patient_name"] = None

    # Example: find patient ID
    m2 = re.search(r"Patient ID[:\s]+([A-Za-z0-9\-]+)", text)
    if m2:
        rec["patient_id"] = m2.group(1).strip()
    else:
        rec["patient_id"] = None

    # You can add more extraction rules as needed:
    # e.g. date of symptom start, location, etc.

    return rec

def normalize_record(rec: dict) -> dict:
    """
    Clean up, format and normalize the extracted record fields.
    For example: unify date formats, default values, etc.
    """
    # Example normalization
    if "patient_name" in rec and rec["patient_name"]:
        rec["patient_name"] = rec["patient_name"].title()
    else:
        rec["patient_name"] = rec.get("patient_name", "")
    # You can normalize dates, clean whitespace, etc.
    return rec
