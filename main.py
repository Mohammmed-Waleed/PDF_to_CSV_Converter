import pandas as pd
import os
import requests
from pdf_parser import extract_sections_from_pdf
from utils import get_box_direct_download, download_pdf

# API endpoint
API_URL = "https://dealerpred.tpvai.com/api/domain_prediction"

def get_ai_wrapups(text: str):
    """Send text to AI API and return wrapup1 and wrapup2"""
    if not text or text.strip() == "":
        return None, None
    
    try:
        response = requests.post(API_URL, json={"complaint": text}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            wrap1 = data.get("AI-Wrapup1")
            wrap2 = data.get("AI-Wrapup2")
            return wrap1, wrap2
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"Failed to call API: {e}")
        return None, None

# Read PDF URLs and filenames
pdf_urls_csv = "pdf_urls.csv"
df_urls = pd.read_csv(pdf_urls_csv, header=None)

keywords = [
    "Question",
    "Situation",
    "Affected models",
    "Implementation Country & Site",
    "Date of Initial CR Request",
    "Answer"
]

all_sections = []

# Process each PDF
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
        result["url"] = url

        # Skip if "AVA" or "MNT" appear anywhere (case-sensitive)
        cell_values = [str(v) for v in result.values()]
        if any("AVA" in cell or "MNT" in cell for cell in cell_values):
            print(f"Skipping {file_name} because it contains 'AVA' or 'MNT'")
        else:
            # 🔹 Call AI API for Question
            question_text = sections.get("Question", "")
            q_wrap1, q_wrap2 = get_ai_wrapups(question_text)
            result["AI-Wrapup1(Question)"] = q_wrap1
            result["AI-Wrapup2(Question)"] = q_wrap2

            # 🔹 Call AI API for Situation
            situation_text = sections.get("Situation", "")
            s_wrap1, s_wrap2 = get_ai_wrapups(situation_text)
            result["AI-Wrapup1(Situation)"] = s_wrap1
            result["AI-Wrapup2(Situation)"] = s_wrap2

            all_sections.append(result)

        os.remove(pdf_path)  # cleanup
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Save to CSV
output_csv = "extracted_sections_filtered.csv"
df_out = pd.DataFrame(all_sections)
df_out.to_csv(output_csv, index=False, encoding="utf-8")
print(f"All extracted data saved to {output_csv}")
