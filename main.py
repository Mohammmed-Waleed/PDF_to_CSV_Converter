import fitz  # PyMuPDF
import pandas as pd
import os

def extract_sections_from_pdf(pdf_path, keywords):
    doc = fitz.open(pdf_path)
    full_text = ""

    # Extract plain text from all pages
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # Normalize spaces
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    sections = {key: "" for key in keywords}
    current_key = None

    for line in lines:
        for key in keywords:
            if line.lower().startswith(key.lower()):
                current_key = key
                sections[current_key] = line.replace(key, "").strip()
                break
        else:
            if current_key:
                sections[current_key] += " " + line

    return sections

# Process all PDFs in DataBase folder and collect results
pdf_folder = "DataBase"
keywords = ["Question", "Situation", "Affected models", "Answer"]
all_sections = []

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        sections = extract_sections_from_pdf(pdf_path, keywords)
        sections["source_file"] = filename  # Optionally add filename for reference
        all_sections.append(sections)

# Save all results to a single CSV file
output_csv = "extracted_sections_all.csv"
df = pd.DataFrame(all_sections)
df.to_csv(output_csv, index=False, encoding="utf-8")
print(f"All extracted data saved to {output_csv}")