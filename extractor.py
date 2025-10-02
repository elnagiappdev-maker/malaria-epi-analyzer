# extractor.py
import re
import json
from form_structure import FORM_STRUCTURE

def extract_fields_from_text(raw_text):
    extracted = {}
    lower_text = raw_text.lower()

    for field_key, field_info in FORM_STRUCTURE.items():
        arabic_q = field_info.get("arabic")
        english_q = field_info.get("english")

        # Build a pattern that matches either Arabic or English
        pattern = rf"(?:{re.escape(arabic_q)}|{re.escape(english_q)}):?\s*(.*)"

        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            extracted[field_key] = value
        else:
            extracted[field_key] = ""

    return extracted

def normalize_record(raw_fields):
    record = {}
    for k, v in raw_fields.items():
        record[k] = v.strip() if isinstance(v, str) else v
    return record
