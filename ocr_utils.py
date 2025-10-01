# ocr_utils.py
import requests
import fitz  # PyMuPDF
import io

def split_pdf_pages(pdf_file):
    """Split a PDF into separate pages and return as list of binary page buffers"""
    pages = []
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page_num in range(len(doc)):
            pdf_writer = fitz.open()
            pdf_writer.insert_pdf(doc, from_page=page_num, to_page=page_num)
            buf = io.BytesIO()
            pdf_writer.save(buf)
            pages.append(buf.getvalue())
    return pages

def group_pages(pages, group_size=4):
    """Group pages in chunks (e.g., every 4 pages = 1 form)"""
    return [pages[i:i+group_size] for i in range(0, len(pages), group_size)]

def ocr_from_file_grouped(uploaded_file, api_key, languages="eng,ara"):
    """Split, group, and OCR a file by chunks (e.g. 4-page malaria form)"""
    split_pages = split_pdf_pages(uploaded_file)
    grouped = group_pages(split_pages, group_size=4)
    
    group_texts = []

    for idx, group in enumerate(grouped):
        text_per_group = []
        for i, page_bytes in enumerate(group):
            response = requests.post(
                url="https://api.ocr.space/parse/image",
                files={"file": ("page.pdf", page_bytes)},
                data={
                    "apikey": api_key,
                    "language": languages,
                    "OCREngine": "2",
                    "isOverlayRequired": False,
                    "scale": True,
                    "isTable": True
                },
            )
            result = response.json()
            parsed = result.get("ParsedResults", [{}])[0].get("ParsedText", "")
            text_per_group.append(parsed)
        group_texts.append("\n".join(text_per_group))
    return group_texts
