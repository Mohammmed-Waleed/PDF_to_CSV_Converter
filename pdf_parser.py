import fitz
import re
from datetime import datetime

def extract_sections_from_pdf(pdf_path, keywords):
    """
    Extracts specific sections from a PDF file based on a list of keywords,
    ensuring dates are formatted as DD/MM/YYYY, accepting formats:
    DD/MM/YYYY, MM/DD/YYYY, YYYY/MM/DD.

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

    # Extraction for "Date of Initial CR Request"
    if "Date of Initial CR Request" in keywords:
        match = re.search(
            r"Date of Initial CR(?: Request)?.*?([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{4})",
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            raw_date = match.group(1)
            cleaned_date = raw_date.replace("-", "/").strip()
            date_obj = None

            # Try parsing with DD/MM/YYYY
            try:
                date_obj = datetime.strptime(cleaned_date, "%d/%m/%Y")
            except ValueError:
                pass
            
            # If parsing failed, try MM/DD/YYYY
            if not date_obj:
                try:
                    date_obj = datetime.strptime(cleaned_date, "%m/%d/%Y")
                except ValueError:
                    pass
            
            # If parsing failed, try YYYY/MM/DD
            if not date_obj:
                try:
                    date_obj = datetime.strptime(cleaned_date, "%Y/%m/%d")
                except ValueError:
                    pass
            
            # If successfully parsed, format to DD/MM/YYYY
            if date_obj:
                sections["Date of Initial CR Request"] = date_obj.strftime("%d/%m/%Y")
            else:
                # If parsing failed, store the cleaned date as-is
                sections["Date of Initial CR Request"] = cleaned_date

    # Extraction for "Implementation Country & Site"
    if "Implementation Country & Site" in keywords:
        match = re.search(
            r"Implementation\s*Country\s*&\s*Site[\s\"'.,]*(\w+)",
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            sections["Implementation Country & Site"] = match.group(1)

    return sections
