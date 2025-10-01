# ocr_utils.py

import fitz  # PyMuPDF
import io
from typing import List, Union
from PIL import Image
import requests

API_URL = "https://api.ocr.space/parse/image"
GROUP_SIZE = 4  # pages per malaria patient form

def pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images

def _post_ocr_image(image: Image.Image, filename: str, api_key: str, language: str = "eng,ara") -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    files = {"file": (filename, buf)}
    data = {
        "language": language,
        "isOverlayRequired": False,
        "OCREngine": 2,
        "scale": True,
        "isTable": True
    }
    headers = {"apikey": api_key}
    resp = requests.post(API_URL, data=data, files=files, headers=headers, timeout=300)
    resp.raise_for_status()
    j = resp.json()
    if j.get("IsErroredOnProcessing"):
        error_msg = j.get("ErrorMessage") or j.get("ErrorDetails") or "OCR Error"
        raise RuntimeError(f"OCR Error: {error_msg}")
    return j["ParsedResults"][0]["ParsedText"]

def ocr_from_file_grouped(
    uploaded_file: Union[object, bytes],
    api_key: str,
    languages: str = "eng,ara",
    group_size: int = GROUP_SIZE
) -> List[str]:
    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(0)
    file_bytes = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    filename = getattr(uploaded_file, "name", "upload").lower()
    results = []
    if filename.endswith(".pdf"):
        images = pdf_to_images(file_bytes)
        for i in range(0, len(images), group_size):
            chunk_images = images[i : i + group_size]
            chunk_texts = []
            for j, img in enumerate(chunk_images):
                try:
                    t = _post_ocr_image(img, f"page_{i+j+1}.png", api_key, languages)
                    chunk_texts.append(t)
                except Exception as e:
                    chunk_texts.append(f"[ERROR on page {i+j+1}]: {e}")
            merged = "\n\n".join(chunk_texts)
            results.append(merged)
    else:
        img = Image.open(io.BytesIO(file_bytes))
        t = _post_ocr_image(img, filename, api_key, languages)
        results.append(t)
    return results
