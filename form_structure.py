# form_structure.py

FORM_STRUCTURE = [
    {
        "section": "Case Identification / تعريف الحالة",
        "fields": [
            ("Case ID", "معرف الحالة"),
            ("Date of Notification", "تاريخ التبليغ"),
            ("Patient Name", "اسم المريض"),
            ("Sex", "الجنس"),
            ("Age", "العمر"),
            ("Nationality", "الجنسية"),
            ("ID Number", "الرقم القومي"),
            ("Phone Number", "رقم الهاتف"),
        ],
    },
    {
        "section": "Residence Information / معلومات السكن",
        "fields": [
            ("State", "الولاية"),
            ("Locality", "المحلية"),
            ("Administrative Unit", "الوحدة الادارية"),
            ("Village/Neighborhood", "القرية/الحي"),
        ],
    },
    {
        "section": "Clinical Information / معلومات سريرية",
        "fields": [
            ("Date of Onset", "تاريخ ظهور الأعراض"),
            ("Date of Diagnosis", "تاريخ التشخيص"),
            ("Diagnosis Facility", "موقع التشخيص"),
            ("Diagnosis Method", "طريقة التشخيص"),
            ("Treatment Given", "العلاج المقدم"),
            ("Hospitalized", "تم إدخاله للمستشفى"),
        ],
    },
    {
        "section": "Epidemiological Investigation / التقصي الوبائي",
        "fields": [
            ("Travel History", "تاريخ السفر"),
            ("Visited Endemic Area", "زيارة لمنطقة موبوءة"),
            ("Other Family Cases", "حالات أخرى في الأسرة"),
            ("Mosquito Nets Used", "استخدام الناموسيات"),
            ("IRS Done", "تم الرش"),
        ],
    },
    {
        "section": "Additional Notes / ملاحظات إضافية",
        "fields": [
            ("Remarks", "ملاحظات"),
        ],
    },
]
