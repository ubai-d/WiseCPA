import requests
def download_form_bytes(form_code):
    """
    Download a form from IRS website and return the PDF bytes without saving locally.
    This prevents the project from becoming huge with stored forms.
    """
    url = f"https://www.irs.gov/pub/irs-pdf/{form_code}.pdf"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.content
        else:
            print(f"❌ Form not found: {form_code}")
            return None
    except Exception as e:
        print(f"⚠️ Error downloading {form_code}: {e}")
        return None

