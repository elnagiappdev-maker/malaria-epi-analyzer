def map_ocr_to_form(record):
    # Example mapping from OCR keys to bilingual Excel columns
    return {
        "Patient Name / اسم المريض": record.get("patient_name", ""),
        "Date of Birth / تاريخ الميلاد": record.get("dob", ""),
        "Gender / الجنس": record.get("gender", ""),
        "Nationality / الجنسية": record.get("nationality", ""),
        "Symptoms / الأعراض": record.get("symptoms", ""),
        "Lab Result / نتيجة المعمل": record.get("lab_result", ""),
        "Diagnosis / التشخيص": record.get("diagnosis", ""),
        "Treatment / العلاج": record.get("treatment", ""),
        "Investigator / المحقق": record.get("investigator", "")
    }
