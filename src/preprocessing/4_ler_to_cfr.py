import os
import shutil
import pandas as pd

INPUT_CSV = "../../data/processed/ler_cfr_empty.csv"
RAW_LER_DIR = "../../data/raw/ler/"
FILTERED_DIR = "../../data/processed/ler_filtered/"

os.makedirs(FILTERED_DIR, exist_ok=True)

df = pd.read_csv(INPUT_CSV, encoding="utf-8")

for fname in df["filename"]:
    pdf_name = f"{fname}.pdf"
    src_path = os.path.join(RAW_LER_DIR, pdf_name)
    dst_path = os.path.join(FILTERED_DIR, pdf_name)

    if os.path.exists(src_path):
        shutil.copy(src_path, dst_path)
        print(f"Copied {pdf_name} to {FILTERED_DIR}")
    else:
        print(f"File not found: {pdf_name}")
