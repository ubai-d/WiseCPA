#!/bin/bash

echo "Setting up WiseCPA AI environment..."

# Step 1: Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Step 2: Create new virtual environment
echo "Creating new virtual environment (venv)..."
python3 -m venv venv

# Step 3: Activate virtual environment
source venv/bin/activate

# Step 4: Ensure pip is upgraded and working
echo "Upgrading pip and setuptools..."
python -m ensurepip --upgrade
pip install --upgrade pip setuptools wheel

# Step 5: Install required dependencies including fpdf
echo "Installing Python packages..."
pip install \
    streamlit \
    openai \
    pytesseract \
    Pillow \
    pdfplumber \
    python-dotenv \
    tiktoken \
    fpdf \
    pandas \
    watchdog

# Step 6: Check for Tesseract OCR
echo "Checking for Tesseract OCR installation..."
if ! command -v tesseract &> /dev/null; then
    echo "Tesseract is not installed."
    echo "Install with:"
    echo "  brew install tesseract          # macOS"
    echo "  sudo apt install tesseract-ocr  # Ubuntu/Debian"
    exit 1
else
    echo "Tesseract found at: $(which tesseract)"
fi

# Step 7: Create .env.example file
echo "Creating .env.example file..."
cat <<EOF > .env.example
# Rename this file to .env and insert your actual OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here
EOF

# Step 8: Final Instructions
echo ""
echo "Setup complete."
echo "Next steps:"
echo "1. Copy .env.example to .env and add your OpenAI API key."
echo "2. Activate the environment: source venv/bin/activate"
echo "3. Run the app: streamlit run app/main.py"
