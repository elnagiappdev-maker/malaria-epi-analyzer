# app.py

import streamlit as st
import pandas as pd
import base64
import datetime
import io
from ocr_utils import ocr_from_file_grouped
from reports import generate_word_report
import matplotlib.pyplot as plt

APP_NAME = "Malaria Epidemiological Analyzer"
DEDICATION_TEXT = "Dedicated to the health professionals serving in endemic areas."

# -- App Config --
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_footer():
    st.markdown(
        """
        <div style='position: fixed; bottom: 0; width: 100%; text-align: center; font-size: small; padding: 10px; background-color: #f9f9f9;'>
        <strong>All rights reserved © Dr. Mohammed Elnagi Mohammed</strong><br>
        <em>{}</em>
        </div>
        """.format(DEDICATION_TEXT),
        unsafe_allow_html=True
    )

def render_chart(data):
    if 'Date of Onset' in data.columns:
        data['Date of Onset'] = pd.to_datetime(data['Date of Onset'], errors='coerce')
        epi_data = data['Date of Onset'].value_counts().sort_index()

        st.subheader("Epi Curve")
        fig, ax = plt.subplots(figsize=(10, 4))
        epi_data.plot(kind='bar', ax=ax)
        ax.set_title("Cases Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Cases")
        st.pyplot(fig)

def render_table(df):
    st.subheader("Structured Data")
    st.dataframe(df)

    # -- Export to Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Malaria Data")
    excel_data = excel_buffer.getvalue()
    st.download_button("Download Excel", data=excel_data, file_name="malaria_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # -- Export to Word
    word_buffer = generate_word_report(df)
    st.download_button("Download Word Report", data=word_buffer, file_name="malaria_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

def render_app():
    st.title(APP_NAME)
    st.markdown("Upload Malaria Investigation Form (PDF). The app will extract and structure the data.")

    uploaded_file = st.file_uploader("Upload multi-page PDF form (each patient = 4 pages)", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Processing... This might take a minute."):
            try:
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_file.read())
                records = ocr_from_file_grouped("temp.pdf")

                if not records:
                    st.error("No data extracted. Please check the PDF format.")
                    return

                df = pd.DataFrame(records)
                render_table(df)
                render_chart(df)
            except Exception as e:
                st.error(f"Processing failed: {e}")

    show_footer()

# Run the app
if __name__ == "__main__":
    render_app()
