import pdfplumber
import re
import os
import pandas as pd
from tqdm import tqdm

def clean_text(text):
    """
    Cleans the extracted text by removing unwanted artifacts.
    """
    # Remove artifacts like (cid:9) and extra spaces
    cleaned_text = re.sub(r"\(cid:\d+\)", " ", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text

def extract_fields_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Combine text from all pages
        full_text = "\n".join(page.extract_text() for page in pdf.pages)

    # Clean the text
    full_text = clean_text(full_text)

    # Extract fields using regular expressions
    fields = {}

    # Facility Name
    facility_name_match = re.search(r"Vogtle Electric Generating Plant.*?Unit \d", full_text, re.IGNORECASE)
    fields["Facility Name"] = (
        facility_name_match.group(0).strip() if facility_name_match else "Not Found"
    )

    # Title
    title_match = re.search(r"Title\s*:?\s*(.*?)(?=Licensee Event Report|LER Number)", full_text, re.IGNORECASE)
    fields["Title"] = title_match.group(1).strip() if title_match else "Not Found"

    # LER Number
    ler_number_match = re.search(r"(\d{4}-\d{3}-\d{2})", full_text)
    fields["LER Number"] = ler_number_match.group(1) if ler_number_match else "Not Found"

    # Event Date
    event_date_match = re.search(
        r"Event Date.*?\b(\d{2})\s+(\d{2})\s+(\d{4})\b", full_text, re.IGNORECASE
    )
    fields["Event Date"] = (
        f"{event_date_match.group(1)}/{event_date_match.group(2)}/{event_date_match.group(3)}"
        if event_date_match
        else "Not Found"
    )

    # Abstract
    abstract_match = re.search(
        r"Abstract\s*[:\-]?\s*(.*?)(?=Narrative|Event Description)", full_text, re.IGNORECASE | re.DOTALL
    )
    fields["Abstract"] = (
        abstract_match.group(1).strip() if abstract_match else "Not Found"
    )

    # Narrative
    narrative_match = re.search(
        r"Narrative\s*[:\-]?\s*(.*?)(?=Event Analysis|Reportability)", full_text, re.IGNORECASE | re.DOTALL
    )
    fields["Narrative"] = (
        narrative_match.group(1).strip() if narrative_match else "Not Found"
    )

    # CFR
    cfr_match = re.search(r"50\.\d{2}\(a\)\(\d\)\(iv\)\(A\)", full_text)
    fields["CFR"] = cfr_match.group(0) if cfr_match else "Not Found"

    return fields

def process_all_pdfs(raw_dir, output_csv_path):
    # List all PDF files in the directory
    pdf_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".pdf")]

    # Create a list to hold extracted data
    extracted_data = []

    # Process each PDF file with progress bar
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join(raw_dir, pdf_file)
        fields = extract_fields_from_pdf(pdf_path)
        fields["File Name"] = pdf_file  # Add file name to the data
        extracted_data.append(fields)

    # Convert to a DataFrame
    df = pd.DataFrame(extracted_data)

    # Save to CSV
    df.to_csv(output_csv_path, index=False, encoding="utf-8")

# Paths
RAW_LER_DIR = "../../data/raw/ler"
OUTPUT_CSV_PATH = "../../data/processed/ler_cfr_mapping.csv"

# Process all PDFs and save the results
process_all_pdfs(RAW_LER_DIR, OUTPUT_CSV_PATH)