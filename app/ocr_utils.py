import pdfplumber
import pytesseract
from PIL import Image
import re
from typing import Tuple

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    else:
        return extract_text_from_image(uploaded_file)

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)



def filter_pdf_fields(
    fields: list[dict],
    *,
    min_label_length: int = 3,
    skip_label_regex: str | None = r'^[\.\s–—_-]{0,}$',
   
    skip_terms_in_label: Tuple[str, ...] = ("OMB No", "Tax Return Service", "Page", "Sheet"),
    skip_fieldname_patterns: Tuple[str, ...] = ("Address_ReadOrder", "Line4a‑11_ReadOrder"),
) -> list[dict]:
    """
    Filter out unwanted PDF form fields based on their 'label' and 'field_name'.

    Parameters:
      fields: list of dicts each having at least 'field_name' (str) and 'label' (str)
      min_label_length: smallest label size (after strip) to keep
      skip_label_regex: regex (full‑match) for labels to exclude (e.g. only punctuation)
      skip_terms_in_label: substring terms that if contained in label, should exclude
      skip_fieldname_patterns: substrings in field_name to filter out table‑ or layout‑only fields

    Returns:
      A new list of dicts passing all the filters.
    """
    label_re = re.compile(skip_label_regex) if skip_label_regex else None
    filtered = []
    for f in fields:
        lbl = (f.get('label') or "").strip()
        if not lbl:
            continue
        if len(lbl) < min_label_length:
            continue
        if label_re and label_re.fullmatch(lbl):
            continue
        lw = lbl.lower()
        if any(term.lower() in lw for term in skip_terms_in_label):
            continue
        fn = f.get('field_name', "")
        if any(pat in fn for pat in skip_fieldname_patterns):
            continue
        filtered.append({
            **f,
            'label': re.sub(r'\s+', ' ', lbl)  # normalize internal spaces
        })
    return filtered
