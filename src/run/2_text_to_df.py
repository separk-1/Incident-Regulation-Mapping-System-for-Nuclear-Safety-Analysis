import os
import re
import pandas as pd
from tqdm import tqdm

LER_TEXT_DIR = "../../data/processed/ler_text"
OUTPUT_CSV_PATH = "../../data/processed/ler_df.csv"

def find_line(keyword, lines):
    for i, l in enumerate(lines):
        if keyword.lower() in l.lower():
            return i
    return None

def extract_multi_line_section(lines, start_keyword, stop_keyword):
    start_idx = find_line(start_keyword, lines)
    if start_idx is None:
        return "Not Found"
    start_idx = start_idx + 1
    extracted = []
    for i in range(start_idx, len(lines)):
        if stop_keyword.lower() in lines[i].lower():
            break
        extracted.append(lines[i])
    return " ".join(extracted).strip() if extracted else "Not Found"

def extract_abstract(lines):
    abs_idx = find_line("16. Abstract", lines)
    if abs_idx is None:
        return "Not Found"
    extracted = []
    for l in lines[abs_idx+1:]:
        if "NRC FORM" in l:
            break
        extracted.append(l)
    return " ".join(extracted).strip() if extracted else "Not Found"

def extract_cfr(lines):
    cfr_start = find_line("11. This Report is Submitted Pursuant", lines)
    if cfr_start is None:
        return "Not Found"
    cfr_pattern = re.compile(r"/\s*([0-9]+\.[0-9]+\(a\)\(\d+\)\(iv\)\([A-Za-z]+\))")
    for i in range(cfr_start, len(lines)):
        cm = cfr_pattern.search(lines[i])
        if cm:
            return cm.group(1)
    return "Not Found"

def extract_narrative(lines):
    nar_idx = find_line("NARRATIVE", lines)
    if nar_idx is None:
        return "Not Found"
    extracted = []
    for l in lines[nar_idx+1:]:
        if "NRC FORM 366A" in l:
            break
        extracted.append(l)
    return " ".join(extracted).strip() if extracted else "Not Found"

def process_txt_file(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.replace("(cid:9)", " ").strip() for line in f]

    facility_name = "Not Found"
    title = "Not Found"
    event_date = "Not Found"
    ler_number = "Not Found"
    abstract = "Not Found"
    cfr = "Not Found"
    narrative = "Not Found"

    # 확장자 제거한 파일명
    file_name = os.path.splitext(os.path.basename(txt_path))[0]

    # Facility Name
    idx_fname = find_line("1. Facility Name", lines)
    if idx_fname is not None and idx_fname+1 < len(lines):
        facility_name = lines[idx_fname+1]

    # Title
    title = extract_multi_line_section(lines, "4. Title", "5. Event Date")

    # Abstract
    abstract = extract_abstract(lines)

    # CFR
    cfr = extract_cfr(lines)

    # Narrative
    narrative = extract_narrative(lines)

    # Date/LER Pattern (하이픈 유무 대응)
    date_ler_pattern = re.compile(r"\b(\d{2})\s+(\d{2})\s+(\d{4})\s+(\d{4})(?:\s*-?\s*)(\d{3})(?:\s*-?\s*)(\d{2})\b")
    for l in lines:
        m = date_ler_pattern.search(l)
        if m:
            mm, dd, yyyy = m.group(1), m.group(2), m.group(3)
            event_date = f"{mm}-{dd}-{yyyy}"
            ler_number = f"{m.group(4)}-{m.group(5)}-{m.group(6)}"
            break

    return {
        "Facility Name": facility_name,
        "Title": title,
        "Event Date": event_date,
        #"LER Number": ler_number,
        "Abstract": abstract,
        #"CFR": cfr,
        "Narrative": narrative,
        "File Name": file_name
    }

def process_all_txt(txt_dir, output_csv_path):
    txt_files = [f for f in os.listdir(txt_dir) if f.lower().endswith(".txt")]
    extracted_data = []

    for txt_file in tqdm(txt_files, desc="Processing TXT files", unit="file"):
        txt_path = os.path.join(txt_dir, txt_file)
        fields = process_txt_file(txt_path)
        extracted_data.append(fields)

    df = pd.DataFrame(extracted_data)
    df.to_csv(output_csv_path, index=False, encoding="utf-8")

# 실행
process_all_txt(LER_TEXT_DIR, OUTPUT_CSV_PATH)
