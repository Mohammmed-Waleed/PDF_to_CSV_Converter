import pandas as pd
import os
import requests
from urllib.parse import urlparse
from pdf_parser import extract_sections_from_pdf
from utils import get_box_direct_download, download_pdf

# Read PDF URLs and filenames from pdf_urls.csv
pdf_urls_csv = "pdf_url.csv"
df_urls = pd.read_csv(pdf_urls_csv, header=None)
# Assumes: first column is filename, second column is URL
keywords = ["Question", "Situation", "Affected models", "Implementation Country & Site", "Date of Initial CR Request", "Answer"]
all_sections = []

# Process PDFs from URLs only
for idx, row in df_urls.iterrows():
    file_name = str(row[0])
    url = str(row[1])
    if not url.startswith("http"):
        print(f"Skipping invalid URL in row {idx}: {url}")
        continue
    try:
        pdf_path = download_pdf(url)
        sections = extract_sections_from_pdf(pdf_path, keywords)
        
        result = {"filename": file_name}
        result.update(sections)
        result["url"] = url  # Add the URL as the last column
        all_sections.append(result)
        os.remove(pdf_path)  # Clean up downloaded file
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Save all results to a single CSV file
output_csv = "extracted_sections_all.csv"
df_out = pd.DataFrame(all_sections)
df_out.to_csv(output_csv, index=False, encoding="utf-8")
print(f"All extracted data saved to {output_csv}")
