import os
import requests
import re
from urllib.parse import urlparse

def get_box_direct_download(url):
    """
    Converts a Box.com shared URL to a direct download URL.

    Args:
        url (str): The original Box.com URL.

    Returns:
        str: The direct download URL, or the original URL if it's not a Box.com link.
    """
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

def download_pdf(url, save_folder="temp_pdfs"):
    """
    Downloads a PDF from a given URL and saves it to a local folder.

    Args:
        url (str): The URL of the PDF file.
        save_folder (str): The local folder to save the PDF.

    Returns:
        str: The local path to the downloaded PDF file.
    """
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
