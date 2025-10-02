# Mapping fields with both Arabic and English labels and grouping
FORM_FIELDS = [
    # Section: Patient Information
    {"key": "patient_name", "keywords": ["Name", "اسم المريض"], "section": "Patient Info"},
    {"key": "patient_id", "keywords": ["ID", "رقم المريض"], "section": "Patient Info"},
    {"key": "nationality", "keywords": ["Nationality", "الجنسية"], "section": "Patient Info"},
    {"key": "age", "keywords": ["Age", "العمر"], "section": "Patient Info"},
    {"key": "gender", "keywords": ["Gender", "الجنس"], "section": "Patient Info"},

    # Section: Contact and Address
    {"key": "phone", "keywords": ["Phone", "رقم الهاتف"], "section": "Contact"},
    {"key": "address", "keywords": ["Address", "العنوان"], "section": "Contact"},

    # Section: Clinical
    {"key": "symptom_start", "keywords": ["Date of symptom", "تاريخ بدء الأعراض"], "section": "Clinical"},
    {"key": "symptoms", "keywords": ["Symptoms", "الأعراض"], "section": "Clinical"},
    {"key": "diagnosis_date", "keywords": ["Diagnosis date", "تاريخ التشخيص"], "section": "Clinical"},
    {"key": "species", "keywords": ["Species", "نوع الطفيل"], "section": "Clinical"},

    # Section: Investigation
    {"key": "travel_history", "keywords": ["Travel", "سفر"], "section": "Investigation"},
    {"key": "place_of_travel", "keywords": ["Place of travel", "مكان السفر"], "section": "Investigation"},
    {"key": "contact_with_cases", "keywords": ["Contact", "مخالطة"], "section": "Investigation"},

    # Section: Treatment
    {"key": "treatment_given", "keywords": ["Treatment", "العلاج"], "section": "Treatment"},
    {"key": "outcome", "keywords": ["Outcome", "النتيجة"], "section": "Treatment"},
]

def get_field_by_key(key):
    return next((f for f in FORM_FIELDS if f["key"] == key), None)

def get_all_keys():
    return [f["key"] for f in FORM_FIELDS]

def get_section_for_key(key):
    field = get_field_by_key(key)
    return field["section"] if field else "General"
