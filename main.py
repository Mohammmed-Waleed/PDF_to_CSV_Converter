import fitz  # PyMuPDF
import pandas as pd
import os
import requests

def get_box_direct_download(url):
    # Extract file ID from Box.com URL
    # Example: https://app.box.com/s/<shared_id>/file/<file_id>
    if "box.com" in url and "/file/" in url:
        parts = url.split("/file/")
        file_id = parts[1].split("?")[0]
        # Direct download URL format:
        # https://app.box.com/index.php?rm=box_download_shared_file&shared_name=<shared_id>&file_id=f_<file_id>
        shared_name = url.split("/s/")[1].split("/")[0]
        direct_url = f"https://app.box.com/index.php?rm=box_download_shared_file&shared_name={shared_name}&file_id=f_{file_id}"
        return direct_url
    return url

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

def download_pdf(url, save_folder="temp_pdfs"):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    # Convert Box.com link to direct download if needed
    direct_url = get_box_direct_download(url)
    local_filename = os.path.join(save_folder, url.split("/")[-1].split("?")[0] + ".pdf")
    response = requests.get(direct_url, stream=True)
    response.raise_for_status()
    with open(local_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_filename

# Read PDF URLs from pdf_url.txt
pdf_urls = []
pdf_url_file = "pdf_urls.txt"
if os.path.exists(pdf_url_file):
    with open(pdf_url_file, "r", encoding="utf-8") as f:
        pdf_urls = [line.strip() for line in f if line.strip()]

keywords = ["Question", "Situation", "Affected models", "Answer"]
all_sections = []

# Process PDFs from URLs only
for url in pdf_urls:
    try:
        pdf_path = download_pdf(url)
        sections = extract_sections_from_pdf(pdf_path, keywords)
        sections["source_file"] = url
        all_sections.append(sections)
        os.remove(pdf_path)  # Clean up downloaded file
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Save all results to a single CSV file
output_csv = "extracted_sections_all.csv"
df = pd.DataFrame(all_sections)
df.to_csv(output_csv, index=False, encoding="utf-8")
print(f"All extracted data saved to {output_csv}")