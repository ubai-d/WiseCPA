# WiseCPA – AI Tax Assistant

**WiseCPA** is a modern, AI-powered tax assistant for CPAs and tax professionals. It automates the process of analyzing uploaded tax documents (W-2s, 1099s, crypto receipts, etc.), identifying deductions, recommending IRS forms, and preparing downloadable worksheets — all powered by **Mistral via Ollama**.

---

## Key Features

| Step | Description |
|------|-------------|
| 1️⃣ | Upload tax documents (PDF, image, CSV) |
| 2️⃣ | View IRS-eligible deductions (AI-generated via Mistral) |
| 3️⃣ | Get AI-recommended IRS forms (Form 1040, 8949, SE, etc.) |
| 4️⃣ | Preview each form’s worksheet with extracted fields |
| 5️⃣ | Download pre-filled worksheets (CSV / PDF) |
| 6️⃣ | Auto-download official IRS forms from [irs.gov](https://irs.gov) |
| 7️⃣ | Optional audit trail & PDF generation for review |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Here2ServeU/WiseCPA.git
cd WiseCPA
```

### 2. Install [Ollama](https://ollama.com) + Run Mistral

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run mistral
```

### 3. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app/main.py
```

---

## 📁 Project Structure

```
WiseCPA/
├── app/
│   ├── main.py           # Streamlit interface (7 steps)
│   ├── ai_engine.py      # Mistral-powered deduction + form logic
│   ├── ocr_utils.py      # PDF/image text extraction via OCR
│   ├── irs_forms.py      # Downloads official IRS forms to /irs_forms
├── irs_forms/            # PDF forms fetched from irs.gov
├── Dockerfile            # Container-ready setup
├── requirements.txt
├── README.md
```

---

## Deployment with Docker

```bash
docker build -t wisecpa .
docker run -p 8501:8501 wisecpa
```

---

## Download IRS Forms Automatically

WiseCPA can pull IRS forms on-demand and save them locally:

```bash
python app/irs_forms.py
```

Saved files will appear in the `irs_forms/` directory. Only valid, published forms are downloaded.

---

## Example Use Cases

- CPAs processing dozens of 1099s and receipts in batch
- Self-employed clients needing deduction and form discovery
- Crypto traders needing capital gains support (Form 8949)
- Firms preparing for audits with traceable AI-generated logs

---

## Roadmap

- [x] Ollama + Mistral LLM integration
- [x] Auto IRS form download from IRS.gov
- [ ] E-filing integration (IRS MeF)
- [ ] Multi-user dashboard with saved sessions
- [ ] Secure cloud deployment (Streamlit Sharing or HuggingFace)

---

## License

MIT License  
© 2025 Emmanuel Naweji
