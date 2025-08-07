import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# def run_mistral(prompt: str) -> str:
#     """Call Ollama with Mistral and return the output."""
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "mistral", prompt],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             timeout=180,  # Increased to 3 minutes for complex prompts
#             encoding="utf-8"
#         )
#         print(result.stdout.strip(),"result")
#         return result.stdout.strip()
#     except Exception as e:
#         return f"❌ Error running model: {e}"

def run_openai(prompt: str) -> str:
    """Call OpenAI GPT-4 and return the output."""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert tax professional and CPA with deep knowledge of IRS regulations and tax law."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  
        )        
        result = response.choices[0].message.content.strip()
        return result
        
    except Exception as e:
        return f"❌ Error running model: {e}"

def suggest_deductions(document_text: str) -> str:
    prompt = f"""
You are an expert tax professional with deep knowledge of IRS regulations. Analyze the following tax document and identify ALL IRS-eligible deductions, credits, and income types that are clearly supported by the document content.

IMPORTANT REQUIREMENTS:
- Identify ALL applicable deductions/income types with 100% accuracy
- Include both common and specialized deductions if supported by the data
- Be comprehensive but accurate - only include what is clearly present
- Focus on precision and completeness, not limiting to common items
- Include all relevant income types, deductions, credits, and adjustments

Look for ALL of the following that apply:
- All income types (wages, interest, dividends, self-employment, rental, etc.)
- All deductions (itemized, business, education, medical, etc.)
- All credits (child tax, education, retirement, etc.)
- All adjustments to income
- All special circumstances supported by the data

CRITICAL: Return ONLY deduction/income names, one per line, NO numbers, NO bullets, NO formatting.

Document:
\"\"\"
{document_text[:3000]}
\"\"\"

Deduction/Income names:"""
    
    raw_response = run_openai(prompt)
    
    # Clean up the response - remove numbers, bullets, etc.
    lines = []
    for line in raw_response.split('\n'):
        line = line.strip()
        if line:
            # Remove common list formatting
            import re
            # Remove numbers (1., 2.), bullets (•, -, *), etc.
            cleaned_line = re.sub(r'^[\d]+[\.\)]\s*', '', line)  # Remove "1. " or "1) "
            cleaned_line = re.sub(r'^[•\-\*]\s*', '', cleaned_line)  # Remove "• " or "- " or "* "
            cleaned_line = cleaned_line.strip()
            
            if cleaned_line:
                lines.append(cleaned_line)
    
    # Return all identified deductions (no artificial limit)
    return '\n'.join(lines)

def recommend_forms(document_text: list):
    # Convert deductions list to text for AI analysis
    deductions_text = " ".join(str(item) for item in document_text)
    
    prompt = f"""
You are an expert tax professional with comprehensive knowledge of all IRS forms and schedules. Based on the following deductions and income types identified from a taxpayer's documents, recommend ALL relevant IRS forms and schedules that would be needed to file their tax return.

IMPORTANT REQUIREMENTS:
- Recommend ALL forms that apply to the taxpayer's situation
- Include the main tax return form (Form 1040 for individuals)
- Include all relevant schedules and additional forms
- Be comprehensive and accurate - don't miss any applicable forms
- Focus on forms that are actually needed based on the deductions/income
- Provide the correct IRS form code for downloading

Deductions and income types identified:
\"\"\"
{deductions_text}
\"\"\"

Return the forms in this exact format (one form per line):
Form_1040|f1040 - U.S. Individual Income Tax Return
Schedule_A|f1040sa - Itemized Deductions
Schedule_B|f1040sb - Interest and Ordinary Dividends
Schedule_C|f1040sc - Profit or Loss From Business
Schedule_D|f1040sd - Capital Gains and Losses
[etc.]

CRITICAL: Return ONLY form names, codes, and descriptions in the format shown above, one per line, NO numbers, NO bullets, NO formatting.
"""
    raw_response = run_openai(prompt)
    
    # Parse the AI response into form objects
    forms = []
    for line in raw_response.split('\n'):
        line = line.strip()
        if line and '|' in line and ' - ' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                form_name = parts[0].strip()
                remaining = parts[1].strip()
                if ' - ' in remaining:
                    code_desc = remaining.split(' - ', 1)
                    if len(code_desc) == 2:
                        form_code = code_desc[0].strip()
                        description = code_desc[1].strip()
                        forms.append({
                            "form": form_name,
                            "code": form_code,
                            "desc": description
                        })
    return forms

def fill_pdf_form(pdf_fields: list[dict], user_data: str, form_name: str) -> dict:
    """
    Fill PDF form with user data using AI analysis.
    Processes fields in batches of 50 to avoid token limits.
    """
    import json
    
    combined_form_fields = {}
    combined_semantic_fields = {}
    
    batch_size = 50
    total_fields = len(pdf_fields)
    
    
    for i in range(0, total_fields, batch_size):
        batch_fields = pdf_fields[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_fields + batch_size - 1) // batch_size
        
        
        prompt = f"""
You are an expert at filling IRS tax forms. Analyze the user's data and map it to the appropriate fields for the {form_name} form.

USER DATA:
\"\"\"
{user_data}
\"\"\"

PDF FIELDS WITH LABELS (Batch {batch_num}/{total_batches}):
{batch_fields}

TASK:
1. UNDERSTAND THE FIELD STRUCTURE:
   - Each field has a 'field_name' (like "topmostSubform[0].Page1[0].f1_01[0]") and a 'label' (like "Your first name and middle initial")
   - The LABEL tells you what the field is for
   - The FIELD_NAME is what you must use in the response

2. FIELD MAPPING PROCESS:
   - READ the labels to understand what each field represents
   - EXTRACT relevant data from user_data based on the label meaning
   - RETURN the data using the EXACT field_name, not the label

3. EXAMPLES OF LABEL → FIELD_NAME MAPPING:
   - Label: "Your first name and middle initial" → Use field_name: "topmostSubform[0].Page1[0].f1_04[0]"
   - Label: "Your social security number" → Use field_name: "topmostSubform[0].Page1[0].f1_06[0]"
   - Label: "If joint return, spouse's first name" → Use field_name: "topmostSubform[0].Page1[0].f1_07[0]"

4. DATA EXTRACTION RULES:
   - NAMES: Split full names into first/middle/last based on label context
   - ADDRESSES: Separate street, city, state, zip correctly
   - SSN: Format as XXX-XX-XXXX
   - INCOME: Match amounts to appropriate income fields
   - CHECKBOXES: Set to "Yes" or "No" based on data

CRITICAL RULES:
- READ the labels to understand what each field is for
- USE the field_name (not the label) in your response
- Use ONLY the field names from the PDF fields list above
- Do NOT make up field names
- In form_fields, use the EXACT field_name values from the PDF
- In semantic_fields, use human-readable descriptions
- Be PRECISE about data extraction and field matching
- Output ONLY valid JSON - no markdown, no code blocks, no explanations
- Do NOT add any text before or after the JSON
- Do NOT use single quotes - use double quotes only
- Output must be EXACTLY this format with no variations:

{{
  "form_fields": {{
    "topmostSubform[0].Page1[0].f1_01[0]": "value",
    "topmostSubform[0].Page1[0].f1_02[0]": "value"
  }},
  "semantic_fields": {{
    "human_readable_name": "value",
    "another_readable_name": "value"
  }}
}}

RESPOND WITH ONLY THE JSON OBJECT - NOTHING ELSE.
"""
        
        raw_response = run_openai(prompt)
        
        try:
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("'") and cleaned_response.endswith("'"):
                cleaned_response = cleaned_response[1:-1]
            if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                cleaned_response = cleaned_response[1:-1]
            
            # Parse the JSON
            batch_result = json.loads(cleaned_response)
            
            # Combine results
            if "form_fields" in batch_result:
                combined_form_fields.update(batch_result["form_fields"])
            if "semantic_fields" in batch_result:
                combined_semantic_fields.update(batch_result["semantic_fields"])
                
            
        except Exception as e:
            continue  
    return {
        "form_fields": combined_form_fields,
        "semantic_fields": combined_semantic_fields
    }

