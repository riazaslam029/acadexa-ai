from pathlib import Path

import fitz
import docx2txt
import pytesseract
from PIL import Image


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_text_from_docx(file_path: str) -> str:
    return docx2txt.process(file_path).strip()


def extract_text_from_image(file_path: str) -> str:
    with Image.open(file_path) as image:
        return pytesseract.image_to_string(image).strip()


def extract_text_from_pdf(file_path: str) -> str:
    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text.strip()


def extract_text_from_file(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension in {".png", ".jpeg", ".jpg"}:
        return extract_text_from_image(file_path)

    raise ValueError(f"Unsupported extraction type for '{extension}'")