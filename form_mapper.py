# form_mapper.py

from typing import Dict, List

# Mapping structure (simplified sample) — Expand as needed
FORM_STRUCTURE = [
    {"section": "Section A: Patient Info", "fields": [
        {"ar": "الاسم", "en": "Name"},
        {"ar": "العمر", "en": "Age"},
        {"ar": "الجنس", "en": "Gender"},
    ]},
    {"section": "Section B: Symptoms", "fields": [
        {"ar": "الحمى", "en": "Fever"},
        {"ar": "قشعريرة", "en": "Chills"},
        {"ar": "تاريخ بداية الأعراض", "en": "Symptoms Start Date"},
    ]},
    {"section": "Section C: Lab Results", "fields": [
        {"ar": "فحص الملاريا", "en": "Malaria Test"},
        {"ar": "نوع الطفيل", "en": "Parasite Type"},
    ]}
]

def get_combined_headers() -> List[str]:
    """Return bilingual headers for Excel columns."""
    headers = []
    for section in FORM_STRUCTURE:
        for field in section["fields"]:
            headers.append(f"{field['en']} / {field['ar']}")
    return headers

def extract_fields_from_text(text: str) -> Dict[str, str]:
    """
    Extracts key fields from OCR text and maps them to headers.
    Assumes text is 1 patient's form.
    """
    data = {}
    for section in FORM_STRUCTURE:
        for field in section["fields"]:
            found = extract_value(text, field["ar"])
            if not found:
                found = extract_value(text, field["en"])
            if found:
                col_name = f"{field['en']} / {field['ar']}"
                data[col_name] = found.strip()
    return data

def extract_value(text: str, label: str) -> str:
    """
    Simple heuristic to extract value after a label (like 'Name:')
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if label in line:
            parts = line.split(":")
            if len(parts) > 1:
                return parts[1]
            elif i + 1 < len(lines):
                return lines[i + 1]
    return ""
