# reports.py

from docx import Document
from docx.shared import Inches
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

def generate_word_report(data: pd.DataFrame) -> BytesIO:
    document = Document()
    document.add_heading('Malaria Investigation Report', 0)
    document.add_paragraph('Generated automatically by the Malaria Epidemiological Analyzer.')
    
    # Add Table
    document.add_heading('Patient Records', level=1)
    table = document.add_table(rows=1, cols=len(data.columns))
    table.autofit = True
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(data.columns):
        hdr_cells[i].text = col

    for _, row in data.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)

    # Pie Chart by Gender
    if 'Sex الجنس' in data.columns:
        gender_counts = data['Sex الجنس'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        pie_image = BytesIO()
        plt.savefig(pie_image, format='png')
        pie_image.seek(0)
        document.add_picture(pie_image, width=Inches(4.5))
        document.add_paragraph('Gender Distribution')

    # Epi Curve
    if 'Date of Onset تاريخ ظهور الاعراض' in data.columns:
        onset_series = pd.to_datetime(data['Date of Onset تاريخ ظهور الاعراض'], errors='coerce')
        curve = onset_series.value_counts().sort_index()
        fig2, ax2 = plt.subplots()
        curve.plot(kind='bar', ax=ax2)
        ax2.set_title('Epi Curve - Cases Over Time')
        ax2.set_xlabel('Date of Onset')
        ax2.set_ylabel('Number of Cases')
        curve_image = BytesIO()
        plt.tight_layout()
        plt.savefig(curve_image, format='png')
        curve_image.seek(0)
        document.add_picture(curve_image, width=Inches(6))
        document.add_paragraph('Epi Curve')

    # Export as BytesIO
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer
