import os, json, io
from datetime import datetime, date
import pandas as pd
import streamlit as st

from extractor import extract_fields_from_text, normalize_record
from validator import validate_record
from reports import generate_word_report, email_file
from ocr_utils import ocr_from_file_grouped as cloud_ocr  # ✅ Use improved OCR

APP_NAME = "Malaria Epidemiological Analyzer"
DEDICATION_TEXT = "To the Soul of my Late Father, My Long Living Mother, My Lovely Wife and My Eyes Abdulrahman & Osman"

# Use secrets for credentials
try:
    VALID_USERNAME = st.secrets["APP_USERNAME"]
    VALID_PASSWORD = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("❌ Application credentials not configured. Please set APP_USERNAME and APP_PASSWORD in Streamlit secrets.")
    st.stop()

st.set_page_config(page_title=APP_NAME, layout="wide")

# ========= Custom Styling ==========
st.markdown("""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg,#f7fafc 0%, #ffffff 80%);
}
.login-wrap { min-height: calc(100vh - 90px); display:flex; align-items:center; justify-content:center; padding:24px 16px; }
.login-card {
  width:100%; max-width:580px;
  background:#ffffff; border:2px solid #1f6feb; border-radius:16px;
  box-shadow:0 8px 24px rgba(0,0,0,0.12); padding:22px 20px;
}
.app-name { text-align:center; color:#1f6feb; font-weight:800; margin:6px 0 10px 0; font-size: clamp(20px, 4vw, 30px); }
.login-sub { text-align:center; color:#334155; margin-bottom:16px; font-size: clamp(12px, 2.5vw, 15px); }

.app-footer {
  position: relative;
  text-align:center; padding:8px 8px 40px 8px;
  background:#ffffffea; border-top:1px solid #e5e7eb;
}
.footer-rights { font-weight:700; color:#1f6feb; margin-bottom:6px; }
.footer-dedication {
  font-weight:700; color:#0f172a; margin-bottom:8px;
  position: relative; z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

def render_footer():
    st.markdown(
        f'<div class="app-footer">'
        f'<div class="footer-rights">All Rights Reserved to Dr. Mohammedelnagi Mohammed</div>'
        f'<div class="footer-dedication"><b>Dedication:</b> {DEDICATION_TEXT}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ===== Auth =====
def ensure_session():
    if "logged_in" not in st.session_state: 
        st.session_state.logged_in = False
    if "login_error" not in st.session_state: 
        st.session_state.login_error = ""

def check_credentials(u, p): 
    return (u == VALID_USERNAME and p == VALID_PASSWORD)

def render_login():
    st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="app-name">{APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Please enter your credentials to continue.</div>', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("Username", value="", key="login_user")
        p = st.text_input("Password", value="", type="password", key="login_pass")
        submitted = st.form_submit_button("Log in")
        
        if submitted:
            if check_credentials(u, p):
                st.session_state.logged_in = True
                st.session_state.login_error = ""
                st.rerun()
            else:
                st.session_state.login_error = "Invalid username or password."
    
    if st.session_state.login_error: 
        st.error(st.session_state.login_error)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    render_footer()

# ===== Utilities =====
def infer_species(text: str) -> str:
    t = text.lower()
    for k in ["falciparum", "vivax", "ovale", "malariae", "knowlesi"]:
        if k in t: 
            return k.capitalize()
    return "Unknown"

def to_df(records): 
    return pd.DataFrame(records) if records else pd.DataFrame()

# ===== Main App =====
def render_app():
    st.title(APP_NAME)
    st.caption("Secure OCR (cloud API) or Excel ingestion, validation, and reporting.")

    with st.sidebar:
        st.header("Account")
        st.success("Logged in as Admin")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.login_error = ""
            st.rerun()

        st.divider()
        st.header("Actions")
        mode = st.radio("Choose input mode:", ["Upload PDFs (OCR via cloud)", "Upload Excel"], index=0)

        st.divider()
        st.header("Diagnostics")
        ocr_key = st.secrets.get("OCRSPACE_API_KEY", "")
        st.code(f"OCR API key: {'configured' if bool(ocr_key) else 'missing'}", language="bash")

    records = []
    df = pd.DataFrame()

    if mode == "Upload PDFs (OCR via cloud)":
        if not ocr_key:
            st.error("OCRSPACE_API_KEY is not set.")
            render_footer()
            return

        files = st.file_uploader("Upload one or more malaria PDFs or images", 
                                 type=["pdf", "png", "jpg", "jpeg"], 
                                 accept_multiple_files=True)
        if files:
            for f in files:
                with st.spinner(f"OCR processing {f.name}..."):
                    try:
                        pages_text = cloud_ocr(f, api_key=ocr_key, languages="eng,ara")
                        full_text = "\n".join(pages_text)
                        rec = normalize_record(extract_fields_from_text(full_text))
                        rec["raw_text"] = full_text
                        rec["species"] = rec.get("species") or infer_species(full_text)
                        rec["symptom_start"] = rec.get("symptom_start") or None
                        rec["ingest_source"] = f.name
                        rec["created_at"] = datetime.utcnow().isoformat(timespec="seconds")
                        rec["validation_flags"] = json.dumps(validate_record(rec))
                        records.append(rec)
                    except Exception as e:
                        st.error(f"Error processing {f.name}: {str(e)}")
            
            if records:
                df = to_df(records)
                st.success(f"Processed {len(df)} file(s).")
                st.dataframe(df, use_container_width=True)

    else:
        xfile = st.file_uploader("Upload Excel (.xlsx) with malaria records", 
                                 type=["xlsx"], 
                                 accept_multiple_files=False)
        if xfile:
            try:
                df = pd.read_excel(xfile)
                for col in ["patient_name", "patient_id", "species", "symptom_start"]:
                    if col not in df.columns: 
                        df[col] = None
                df["created_at"] = datetime.utcnow().isoformat(timespec="seconds")
                df["validation_flags"] = [json.dumps(validate_record(r.to_dict())) for _, r in df.iterrows()]
                st.success(f"Loaded {len(df)} rows from Excel.")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")

    if not df.empty and "species" in df.columns:
        st.subheader("Species Distribution")
        species_counts = df["species"].fillna("Unknown").value_counts().sort_values(ascending=False)
        st.bar_chart(species_counts)

    if not df.empty:
        st.subheader("Report")
        name = f"malaria_report_{date.today().isoformat()}.docx"
        report_name = st.text_input("Report file name", value=name)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Generate Word report"):
                try:
                    p = generate_word_report(df, report_name)
                    st.success(f"Report saved: {p}")
                    with open(p, "rb") as f:
                        st.download_button("Download report", 
                                           data=f.read(),
                                           file_name=report_name,
                                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as e: 
                    st.error(f"Report generation failed: {e}")
        
        with c2:
            if st.button("Email report via Gmail"):
                try:
                    email_from = st.secrets.get("EMAIL_FROM")
                    email_password = st.secrets.get("EMAIL_PASSWORD")
                    email_to = st.secrets.get("EMAIL_TO")
                    
                    if not all([email_from, email_password, email_to]):
                        st.error("Email configuration incomplete.")
                    else:
                        p = generate_word_report(df, report_name)
                        email_file(p, "Malaria Report Update", email_from, email_password, email_to)
                        st.success("Email sent successfully.")
                except Exception as e: 
                    st.error(f"Email failed: {e}")

        # ✅ FIXED: Excel Download Button
        st.subheader("Download Excel")
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Malaria Records")
        excel_data = excel_buffer.getvalue()
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="malaria_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    render_footer()

# ===== Main Entry =====
def ensure_and_run():
    ensure_session()
    if not st.session_state.logged_in: 
        render_login()
    else: 
        render_app()

if __name__ == "__main__":
    ensure_and_run()
