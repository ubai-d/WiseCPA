import io
import fitz
import tempfile
import os
import tempfile, os
from typing import Any, Dict, List
import fitz

def list_pdf_fields(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """Return a list of dicts with unique widget info: field_name, label"""
    out: List[Dict[str, Any]] = []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes); tmp.flush()
        fp = tmp.name

    try:
        doc = fitz.open(fp)
        for p_idx in range(len(doc)):
            page = doc[p_idx]
            words = sorted(page.get_text("words"), key=lambda w: (-w[1], w[0]))
            widgets = page.widgets() or []
            for widget in widgets:
                wtype = widget.field_type_string.lower()
                if wtype != "text":
                    continue

                xref = widget.xref
                name = widget.field_name or ""
                alt = getattr(widget, "field_label", None)
                label = alt if (alt and alt != name) else ""
                if not label:
                    r = widget.rect
                    sr = fitz.Rect(r.x0 - r.width * 1.5, r.y0 - 30, r.x1, r.y0)
                    near = [w[4] for w in words if fitz.Rect(w[:4]).intersects(sr)]
                    if near:
                        label = " ".join(near[:7]).strip()
                key = f"{p_idx+1}-{xref}"

                out.append({
                    "field_name": name,
                    "label": label,
                })

        doc.close()
    finally:
        try: os.unlink(fp)
        except OSError: pass

    return out


def fill_pdf_form_simple(pdf_bytes: bytes, fields: dict[str, str]) -> bytes:
    """Fill PDF form using PyMuPDF (fitz) with visible updates and exact field match."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        input_path = tmp.name

    try:
        doc = fitz.open(input_path)
        black_color = (0, 0, 0)
        for page in doc:
            widgets = page.widgets()
            if not widgets:
                continue

            for widget in widgets:
                field_name = widget.field_name
                if field_name in fields:
                    widget.field_value = fields[field_name]
                    widget.text_color = black_color
                    widget.update()

        buf = io.BytesIO()
        doc.save(buf, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP, deflate=True)
        doc.close()
        return buf.getvalue()

    finally:
        try:
            os.unlink(input_path)
        except OSError:
            pass
