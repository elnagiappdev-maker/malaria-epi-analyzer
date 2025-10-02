# ocr_utils.py

import fitz  # PyMuPDF
import requests
import base64
import time
import form_mapper  # This imports the mapping module

OCRSPACE_API_KEY = "your_ocr_space_api_key"

def pdf_to_images(pdf_path):
    """Convert PDF to a list of images (one per page)"""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        images.append(pix.tobytes("png"))
    return images

def ocr_image_base64(image_bytes):
    """Send image to OCR.space and return extracted text"""
    base64_img = base64.b64encode(image_bytes).decode()
    payload = {
        "base64Image": "data:image/png;base64," + base64_img,
        "language": "ara,eng",
        "isOverlayRequired": False,
        "OCREngine": 2
    }
    headers = {"apikey": OCRSPACE_API_KEY}
    url = "https://api.ocr.space/parse/image"
    
    response = requests.post(url, data=payload, headers=headers)
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        raise Exception(result.get("ErrorMessage", "OCR failed"))
    return result["ParsedResults"][0]["ParsedText"]

def split_images_into_patients(images, pages_per_patient=4):
    """Group every 4 pages as one patient"""
    return [images[i:i + pages_per_patient] for i in range(0, len(images), pages_per_patient)]

def ocr_from_file_grouped(pdf_path):
    """
    OCR the PDF, group by patient (4 pages per patient), extract structured data
    """
    all_images = pdf_to_images(pdf_path)
    grouped_images = split_images_into_patients(all_images)

    results = []
    for patient_images in grouped_images:
        patient_text = ""
        for img_bytes in patient_images:
            try:
                text = ocr_image_base64(img_bytes)
                patient_text += "\n" + text
                time.sleep(1.5)  # Avoid API rate limit
            except Exception as e:
                print("OCR failed on image:", e)
                continue

        patient_data = form_mapper.extract_fields_from_text(patient_text)
        if patient_data:
            results.append(patient_data)

    return results
