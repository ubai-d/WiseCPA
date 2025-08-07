import streamlit as st
import pandas as pd
import re
from io import BytesIO
from ocr_utils import extract_text_from_file
from ai_engine import suggest_deductions, recommend_forms, fill_pdf_form
from fpdf import FPDF
from irs_forms import download_form_bytes
from pdf_filler import list_pdf_fields, fill_pdf_form_simple
from ocr_utils import filter_pdf_fields

st.set_page_config(page_title="WiseCPA – AI Tax Assistant", layout="wide")

st.markdown("""
# 🧠 WiseCPA – AI Tax Assistant  
Upload client tax documents to get:
- AI-generated IRS deductions
- Smart form recommendations
- Previews + downloadable worksheets (CSV/PDF)
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "📤 Upload tax documents (W-2, 1099, crypto, receipts):",
    type=["pdf", "jpg", "png", "csv", "jpeg"],
    accept_multiple_files=True,
)

if "recommended_forms_ai" not in st.session_state:
    st.session_state.recommended_forms_ai = []
if "auto_filled_data" not in st.session_state:
    st.session_state.auto_filled_data = {}
if "downloaded_pdf" not in st.session_state:
    st.session_state.downloaded_pdf = None
if "filled_pdf" not in st.session_state:
    st.session_state.filled_pdf = None

# === Helpers ===
def normalize_label(label: str) -> str:
    return re.sub(r"_", " ", label).title()

def create_table_preview(data: dict) -> pd.DataFrame:
    rows = [{"Field Name": normalize_label(k), "Sample Value": v} for k, v in data.items()]
    return pd.DataFrame(rows)

def download_csv_or_pdf(form_name, df, file_format):
    buffer = BytesIO()
    if file_format == "CSV":
        df.to_csv(buffer, index=False)
    elif file_format == "PDF":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Worksheet: {form_name}", ln=True)
        pdf.set_font("Arial", size=12)
        for i, row in df.iterrows():
            pdf.cell(0, 10, f"{row['Field Name']}: {row['Sample Value']}", ln=True)
        buffer.write(pdf.output(dest='S').encode("latin1"))
    buffer.seek(0)
    return buffer

if uploaded_files:
    st.success(f"✔ {len(uploaded_files)} documents uploaded successfully.")
    extracted_text = "\n".join([extract_text_from_file(file) for file in uploaded_files])

    tabs = st.tabs([
        "Step 2: Deductions",
        "Step 3: IRS Recommended Forms",
        "Step 4: IRS Form Preview",
        "Step 5: Download Worksheets"
    ])

    with tabs[0]:
        st.subheader("✅ Step 2: IRS-Eligible Deductions")
        if st.button("Generate Deductions"):
            try:
                with st.spinner("Analyzing your tax documents... This may take few moments"):
                    raw = suggest_deductions(extracted_text)
                lines = [line.strip() for line in raw.split("\n") if line.strip()]

                st.markdown("""
Based on the analysis of the uploaded documents, the following IRS-eligible deduction-related fields were identified:
""")

                deduced_table = pd.DataFrame([[i+1, normalize_label(line)] for i, line in enumerate(lines)], columns=["#", "Deduction"])
                st.dataframe(deduced_table, use_container_width=True)
                st.session_state.step2_deductions = lines
            except Exception as e:
                st.error(f"Error generating deductions: {e}")

    with tabs[1]:
        st.subheader("📑 Step 3: IRS Recommended Forms")
        if st.button("Get Form Suggestions"):
            try:
                with st.spinner("Analyzing deductions for relevant IRS forms..."):
                    ai_deductions = st.session_state.get('step2_deductions', [])
                    if ai_deductions:
                        forms = recommend_forms(ai_deductions)
                    
                if isinstance(forms, dict):
                    forms = [forms]
                st.session_state.recommended_forms_ai = forms
                for f in forms:
                    st.markdown(f"**{f['form']}** – {f.get('desc','')}")
            except Exception as e:
                st.error(f"Form recommendation failed: {e}")

    with tabs[2]:
        st.subheader("📋 Step 4: IRS Form Preview")
        form_options = [f["form"] for f in st.session_state.recommended_forms_ai]
        if form_options:
            selected = st.selectbox("Select IRS Form", form_options)
            if st.button("Generate Preview"):
                try:
                    with st.spinner("Downloading form and filling with your data..."):
                        selected_form_data = next((f for f in st.session_state.recommended_forms_ai if f["form"] == selected), None)
                        
                        if selected_form_data and "code" in selected_form_data:
                            form_code = selected_form_data["code"]
                            form_desc = selected_form_data.get("desc", "")
                            
                            pdf_bytes = download_form_bytes(form_code)
                            
                            if pdf_bytes:
                                user_data = extracted_text
                                pdf_fields = list_pdf_fields(pdf_bytes)
                                filtered_pdf_fields = filter_pdf_fields(pdf_fields)
                                field_mapping = fill_pdf_form(filtered_pdf_fields, user_data, selected)
                                semantic_fields = field_mapping.get("semantic_fields", {})
                                form_fields = field_mapping.get("form_fields", {})
                                filled_pdf_bytes = fill_pdf_form_simple(pdf_bytes, form_fields)
                                if semantic_fields:
                                    st.subheader("Extracted Data Summary")                                    
                                    semantic_data = []
                                    for field_name, value in semantic_fields.items():
                                        semantic_data.append([field_name, value])
                                    
                                    if semantic_data:
                                        semantic_df = pd.DataFrame(semantic_data, columns=["Field", "Value"])
                                        st.dataframe(semantic_df, use_container_width=True)                                
                                st.session_state.filled_pdf = filled_pdf_bytes
                                st.session_state.form_name = selected
                                st.session_state.semantic_fields = semantic_fields
                except Exception as e:
                    st.error(f"Error processing form: {e}")
        else:
            st.warning("No IRS forms suggested. Complete Step 3 first.")

    with tabs[3]:
        st.subheader("📥 Step 5: Download Filled Form")
        if hasattr(st.session_state, 'filled_pdf') and st.session_state.filled_pdf is not None:            
            form_name = getattr(st.session_state, 'form_name', 'Unknown Form')
            
            # Dropdown to select download format
            download_format = st.selectbox(
                "Select Download Format:",
                ["PDF Form", "CSV Data"],
                help="Choose between the filled PDF form or extracted data as CSV"
            )
            
            # Download button based on selection
            if download_format == "PDF Form":
                st.download_button(
                    label="⬇️ Download Filled PDF Form",
                    data=st.session_state.filled_pdf,
                    file_name=f"{form_name}_filled.pdf",
                    mime="application/pdf",
                    help="Download the filled tax form with your data"
                )
                
            elif download_format == "CSV Data":
                if hasattr(st.session_state, 'semantic_fields') and st.session_state.semantic_fields:
                    semantic_df = pd.DataFrame([
                        {"Field": field, "Value": value} 
                        for field, value in st.session_state.semantic_fields.items()
                    ])
                    
                    csv_buffer = BytesIO()
                    semantic_df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Download Data CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"{form_name}_extracted_data.csv",
                        mime="text/csv",
                        help="Download the extracted data as CSV"
                    )
                else:
                    st.warning("⚠️ No filled form available. Please complete Step 4 first to generate a filled form.")
                    st.info("📋 Go to Step 4: IRS Form Preview to generate and fill a form with your data.")
else:
    st.info("📤 Please upload your tax documents to begin.")
