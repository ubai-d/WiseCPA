# Placeholder for advanced file parsing logic
def parse_uploaded_file(file):
    return file.read().decode("utf-8") if hasattr(file, "read") else str(file)
