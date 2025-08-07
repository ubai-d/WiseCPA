#!/bin/bash

echo "Cleaning up WiseCPA  project..."

# Step 1: Deactivate virtualenv if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

# Step 2: Remove virtual environment folder
if [ -d "venv" ]; then
    echo "Removing virtual environment (.venv)..."
    rm -rf venv
fi

# Step 3: Remove __pycache__ folders
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# Step 4: Remove .env and compiled Python files
echo "Removing .env and *.pyc files..."
rm -f .env
find . -type f -name "*.pyc" -delete

# Step 5: Remove generated forms or temp folders (customize as needed)
if [ -d "generated_forms" ]; then
    echo "Removing generated_forms folder..."
    rm -rf generated_forms
fi

if [ -d "output" ]; then
    echo "Removing output folder..."
    rm -rf output
fi

# Done
echo "Cleanup complete."
