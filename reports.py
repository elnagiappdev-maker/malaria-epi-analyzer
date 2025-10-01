# reports.py

import pandas as pd
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches

def generate_word_report(df: pd.DataFrame, filename: str) -> str:
    doc = Document()
    doc.add_heading("Malaria Epidemiological Report", level=1)
    doc.add_paragraph(f"Date: {pd.Timestamp.now().date().isoformat()}")

    # Pie chart: species distribution
    if "species" in df.columns:
        counts = df["species"].fillna("Unknown").value_counts()
        fig, ax = plt.subplots()
        counts.plot.pie(autopct="%1.1f%%", ax=ax, legend=False)
        ax.set_ylabel("")
        fig.savefig("species_pie.png")
        doc.add_heading("Species Distribution", level=2)
        doc.add_picture("species_pie.png", width=Inches(4))

    # EpiCurve: symptom_start dates
    if "symptom_start" in df.columns:
        df["symptom_start"] = pd.to_datetime(df["symptom_start"], errors="coerce")
        df2 = df.dropna(subset=["symptom_start"])
        if not df2.empty:
            counts = df2.groupby(df2["symptom_start"].dt.date).size()
            fig2, ax2 = plt.subplots(figsize=(5, 3))
            counts.plot(kind="line", marker="o", ax=ax2)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Number of Cases")
            fig2.savefig("epicurve.png")
            doc.add_heading("EpiCurve", level=2)
            doc.add_picture("epicurve.png", width=Inches(5))

    # Add table of first few rows
    doc.add_heading("Data Summary", level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, c in enumerate(df.columns):
        hdr_cells[i].text = str(c)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, c in enumerate(df.columns):
            row_cells[i].text = str(row[c])

    out_path = filename
    doc.save(out_path)
    return out_path

def email_file(path: str, subject: str, from_addr: str, password: str, to_addr: str):
    import smtplib, ssl
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    with open(path, "rb") as f:
        file_data = f.read()
        file_name = path

    msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(from_addr, password)
        smtp.send_message(msg)
