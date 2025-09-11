import fitz
import re

def extract_sections_from_pdf(pdf_path, keywords):
    """
    Extracts specific sections from a PDF file based on a list of keywords.

    Args:
        pdf_path (str): The path to the PDF file.
        keywords (list): A list of keywords representing the sections to extract.

    Returns:
        dict: A dictionary containing the extracted sections.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    # Extract plain text from all pages
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # Normalize spaces
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    sections = {key: "" for key in keywords}
    current_key = None

    for i, line in enumerate(lines):
        for key in keywords:
            if key.lower() in line.lower():  # Relaxed matching
                current_key = key
                cleaned_line = line.lower().replace(key.lower(), "").strip(" :-")
                sections[current_key] = cleaned_line
                break
        else:
            if current_key:
                sections[current_key] += " " + line.strip()

    # Additional extraction for "Date of Initial CR Request" if not found by keyword logic
    if "Date of Initial CR Request" in keywords and not sections["Date of Initial CR Request"]:
        # The regular expression has been updated to be much more robust
        # and handle unexpected characters and spacing, including newlines.
        match = re.search(
            r"Date of Initial CR(?: Request)?.*?([0-9]{2}/[0-9]{2}/[0-9]{4})",
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            sections["Date of Initial CR Request"] = match.group(1)
            
    # Correct extraction for "Implementation Country & Site"
    if "Implementation Country & Site" in keywords:
        match = re.search(
            r"Implementation\s*Country\s*&\s*Site[\s\"'.,]*(\w+)",
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            sections["Implementation Country & Site"] = match.group(1)
            

    return sections
