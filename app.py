import streamlit as st
import pandas as pd
import base64
import io
from reports import generate_word_report
from ocr_utils import ocr_from_file_grouped
from extractor import extract_fields_from_text, normalize_record
from validator import validate_record
from form_mapper import map_ocr_to_form

APP_USERNAME = "admin"
APP_PASSWORD = "malaria2025"

def show_login():
    st.title("🔐 Malaria Epidemiological Analyzer")
    with st.form("login_form", clear_on_submit=False):
        st.write("Please login to continue.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    # Dedication styled and below login box
    st.markdown("""
    <div style='margin-top: 40px; padding: 10px; color: darkblue; font-size: 16px; font-weight: bold;'>
    Dedication: To the Soul of my late father Abdulrahman, my long living mother Zainab, my beloved wife Yousra and my eyes, Abdulrahman & Osman.
    </div>
    """, unsafe_allow_html=True)
    # Footer
    st.markdown("""
    <div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: gray;'>
    All rights reserved © Dr. Mohammedelnagi Mohammed
    </div>
    """, unsafe_allow_html=True)

def render_app():
    st.title("📄 Malaria Case Investigation Form Processor")

    uploaded_files = st.file_uploader("Upload Malaria Investigation PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        all_results = []
        for pdf_file in uploaded_files:
            ocr_texts = ocr_from_file_grouped(pdf_file)
            for patient_pages in ocr_texts:
                combined_text = "\n".join(patient_pages)
                raw_record = extract_fields_from_text(combined_text)
                normalized = normalize_record(raw_record)
                validated = validate_record(normalized)
                form_row = map_ocr_to_form(validated)
                all_results.append(form_row)

        df = pd.DataFrame(all_results)

        # Download buttons
        st.download_button("📥 Download Excel", convert_df_to_excel(df), file_name="malaria_data.xlsx")
        st.download_button("📄 Download Word Report", generate_word_report(df), file_name="malaria_report.docx")

        # Display dataframe
        st.dataframe(df)

    # Persistent footer
    st.markdown("""
    <div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: gray;'>
    All rights reserved © Dr. Mohammedelnagi Mohammed
    </div>
    """, unsafe_allow_html=True)

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Data"]
        watermark_format = workbook.add_format({'font_color': 'gray', 'font_size': 8})
        worksheet.write("A1", "© Dr. Mohammedelnagi Mohammed", watermark_format)
    output.seek(0)
    return output

def ensure_and_run():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        render_app()
    else:
        show_login()

ensure_and_run()
