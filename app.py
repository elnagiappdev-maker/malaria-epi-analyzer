import streamlit as st
import pandas as pd
from extractor import extract_fields_from_text, normalize_record
from ocr_utils import ocr_from_file_grouped
from reports import generate_excel, generate_word_report
from validator import validate_records

# ---------------------------
# App Credentials & Settings
# ---------------------------
APP_USERNAME = "admin"
APP_PASSWORD = "Elnagi@2026"
DEDICATION_TEXT = (
    "### 🌹 *To the Soul of my late father Abdulrahman, my long living mother Zainab, "
    "my beloved wife Yousra, and my eyes, Abdulrahman & Osman.*"
)
RIGHTS_RESERVED = "© All Rights Reserved – Dr. Mohammedelnagi Mohammed"

st.set_page_config(page_title="Malaria Epi Analyzer", layout="wide")

# ---------------------------
# Session State Init
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------------------
# Login Form
# ---------------------------
def show_login():
    st.markdown("<div style='text-align: center;'>"
                "<h2>🔐 Login Required</h2></div>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        st.write("Please login to continue.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful.")
            else:
                st.error("Invalid username or password")

    st.markdown(f"<div style='text-align: center; color: #C2185B; font-weight: bold;'>{DEDICATION_TEXT}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: gray;'>{RIGHTS_RESERVED}</div>", unsafe_allow_html=True)


# ---------------------------
# Main App Interface
# ---------------------------
def render_app():
    st.title("📊 Malaria Epidemiological Analyzer")

    uploaded_files = st.file_uploader("📄 Upload Malaria Investigation Form(s)", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)

    api_key = st.secrets.get("OCRSPACE_API_KEY", "")

    if not api_key:
        st.warning("⚠️ OCR API key not set. Please add it to your Streamlit secrets.")
        return

    if uploaded_files:
        all_records = []
        errors = []
        for file in uploaded_files:
            try:
                pages = ocr_from_file_grouped(file, api_key=api_key)
                for page_text in pages:
                    fields = extract_fields_from_text(page_text)
                    normalized = normalize_record(fields)
                    all_records.append(normalized)
            except Exception as e:
                errors.append(f"❌ Error processing {file.name}: {str(e)}")

        if errors:
            st.error("\n\n".join(errors))

        if all_records:
            df = pd.DataFrame(all_records)

            valid, validation_errors = validate_records(df)

            if not valid:
                st.warning("⚠️ Some records are invalid:")
                st.json(validation_errors)

            st.success(f"✅ Processed {len(all_records)} records")

            # Display table
            st.dataframe(df)

            # Export buttons
            excel_data = generate_excel(df)
            word_data = generate_word_report(df)

            st.download_button("📥 Download Excel", excel_data, file_name="malaria_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.download_button("📥 Download Word Report", word_data, file_name="malaria_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown(f"<div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: gray;'>{RIGHTS_RESERVED}</div>", unsafe_allow_html=True)


# ---------------------------
# App Entry Point
# ---------------------------
def ensure_and_run():
    if st.session_state.logged_in:
        render_app()
    else:
        show_login()

ensure_and_run()
